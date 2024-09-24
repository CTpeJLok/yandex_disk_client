from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.core.cache import cache
from urllib.parse import ParseResult, urlparse, parse_qs, urlencode, urlunparse
from django.views.decorators.csrf import csrf_exempt

import requests
from datetime import datetime
import math
import traceback
import aiohttp
import asyncio
import os
from zipfile import ZipFile
from io import BytesIO
from asgiref.sync import async_to_sync
import json

PER_PAGE = 10


def pagination(total: int, page: int) -> dict[str, bool | int]:
    """
    Calculate pagination info by total files and current page
    """

    page_count = math.ceil(total / PER_PAGE)

    return {
        "is_can_go_back": page > 1,
        "is_can_go_next": page < page_count,
        "page_count": page_count,
    }


def make_drop_cache(request: HttpRequest, cache_key: str) -> HttpResponseRedirect:
    """
    Delete cache and redirect to get new files from Yandex API
    """

    cache.delete(cache_key)

    # remove drop_cache param from url
    current_url: str = request.get_full_path()
    parsed_url: ParseResult = urlparse(current_url)
    query_params: dict = parse_qs(parsed_url.query)
    del query_params["drop_cache"]

    new_query_string: str = urlencode(query_params, doseq=True)
    new_url: str = urlunparse(parsed_url._replace(query=new_query_string))
    return HttpResponseRedirect(new_url)


async def download_file(
    session: aiohttp.ClientSession, url: str, filename: str
) -> tuple[str, bytes] | tuple[None, None]:
    """
    Download file async
    """

    async with session.get(url) as file_response:
        if file_response.status == 200:
            return os.path.basename(filename), await file_response.read()

    return None, None


async def download_files(files: list) -> list[tuple[str, bytes] | tuple[None, None]]:
    """
    Download a lot of files async
    """

    async with aiohttp.ClientSession() as session:
        tasks = [
            download_file(session, file["url"], file["filename"]) for file in files
        ]
        return await asyncio.gather(*tasks)


def download_and_make_zip(files: list) -> HttpResponse:
    """
    Download file or make zip archive if there are many files
    """

    files = async_to_sync(download_files)(files)

    if len(files) > 1:
        zip_buffer = BytesIO()

        with ZipFile(zip_buffer, "w") as zip_file:
            for filename, file_content in files:
                if filename and file_content:
                    zip_file.writestr(filename, file_content)

        zip_buffer.seek(0)

        response = HttpResponse(zip_buffer, content_type="application/zip")
        response["Content-Disposition"] = 'attachment; filename="files.zip"'
    else:
        response = HttpResponse(files[0][1], content_type="application/octet-stream")
        response["Content-Disposition"] = f'attachment; filename="{files[0][0]}"'

    return response


@login_required(login_url="login")
@csrf_exempt
def download_request(request: HttpRequest) -> HttpResponse:
    body = json.loads(request.body)
    files = body.get("files", [])

    return download_and_make_zip(files)


@login_required(login_url="login")
def index(request: HttpRequest) -> HttpResponse:
    url: str | None = request.GET.get("url")
    key: str | None = request.GET.get("key")

    if not url and not key:
        return render(
            request,
            template_name="disk_manager/index.html",
            context={
                "get_info": "Введите ссылку или public_key",
            },
        )

    cache_key: str = f"files2_{url if url else key}"
    is_drop_cache: bool = bool(request.GET.get("drop_cache", 0))
    if is_drop_cache:
        return make_drop_cache(request, cache_key)

    page: int = max(1, int(request.GET.get("page", 1)))

    context = {
        "url": url,
        "key": key,
        "page": page,
    }

    # try to get files fom cache
    from_cache = cache.get(cache_key)
    if from_cache:
        current_files = from_cache.get(page)

        if current_files:
            context["get_info"] = "Получено из кэша"
            context["is_cached"] = True

            context["files"] = current_files
            context["pagination"] = pagination(from_cache["total"], page)

            return render(
                request,
                template_name="disk_manager/index.html",
                context=context,
            )

    # if not in cache, get from api
    if url or key:
        try:
            response = requests.get(
                f"https://cloud-api.yandex.net/v1/disk/public/resources?public_key={url if url else key}&sort=name&limit={PER_PAGE}&offset={(page - 1) * PER_PAGE}",
                headers={
                    "Accept": "application/json",
                },
                timeout=5,
            )

            response.raise_for_status()

            result = response.json()
            embedded = result.get("_embedded", {})
            files = embedded.get("items", [])

            # parse modified
            for file in files:
                file["modified"] = datetime.fromisoformat(file["modified"])

            context["files"] = files
            context["pagination"] = pagination(embedded["total"], page)

            # get cache
            from_cache: dict = cache.get(
                cache_key,
                {
                    "total": embedded["total"],
                },
            )

            # clear cache if total count of files changed
            if from_cache["total"] != embedded["total"]:
                from_cache = {
                    "total": embedded["total"],
                }

            from_cache[page] = files

            # save cache
            cache.set(cache_key, from_cache, timeout=24 * 60 * 60)
        except requests.exceptions.Timeout:
            context["get_error"] = "Время ожидания истекло"
        except requests.exceptions.HTTPError:
            context["get_error"] = "Неверный URL"
        except requests.exceptions.ConnectionError:
            context["get_error"] = "Нет соединения с интернетом"
        except:
            context["get_error"] = f"Ошибка получения файлов: {traceback.format_exc()}"

    return render(
        request,
        template_name="disk_manager/index.html",
        context=context,
    )

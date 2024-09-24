from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest

import requests
from datetime import datetime
import math
import traceback

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


@login_required(login_url="login")
def index(request: HttpRequest):
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

    page: int = max(1, int(request.GET.get("page", 1)))

    context = {
        "url": url,
        "key": key,
        "page": page,
    }

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

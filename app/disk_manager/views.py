from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest

import requests
from datetime import datetime
import traceback


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

    context = {
        "url": url,
        "key": key,
    }

    if url or key:
        try:
            response = requests.get(
                f"https://cloud-api.yandex.net/v1/disk/public/resources?public_key={url if url else key}&sort=name",
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

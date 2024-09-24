from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("account/", include("user_manager.urls")),
    path("", include("disk_manager.urls")),
]

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("django_api.accounts.urls")),
    path("api/", include("django_api.screening.urls")),
]

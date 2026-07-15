"""
Root URL configuration.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    path("accounts/", include("accounts.urls")),
    path("categories/", include("categories.urls")),
    path("units/", include("units.urls")),
    path("suppliers/", include("suppliers.urls")),
    path("products/", include("products.urls")),
    path("stock/", include("stock.urls")),
    path("reports/", include("reports.urls")),
    path("notifications/", include("notifications.urls")),
    path("search/", include("search.urls")),
    path("settings/", include("settings_app.urls")),
    path("", include("dashboard.urls")),
]

# Serve uploaded media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

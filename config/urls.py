"""
Root URL configuration.

MENTOR NOTE (Laravel -> Django):
- This is `routes/web.php`. `path()` ≈ `Route::get()`.
- `include()` mounts another app's urls.py — like Laravel's route groups /
  a modular `Route::middleware(...)->group()` split per feature.
- We register our apps here; Django resolves URLs top-down.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("categories/", include("categories.urls")),
    path("units/", include("units.urls")),
    path("suppliers/", include("suppliers.urls")),
    path("products/", include("products.urls")),
    path("stock/", include("stock.urls")),
    path("", include("dashboard.urls")),
]

# Serve uploaded media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

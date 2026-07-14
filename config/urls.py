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

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("categories/", include("categories.urls")),
    path("", include("dashboard.urls")),
]

"""
Django settings for the Warehouse Inventory Management System.

MENTOR NOTE (Laravel -> Django):
- This file is the equivalent of `config/` in Laravel (app.php, database.php, etc.)
  merged into one module. Django keeps everything in Python (not PHP arrays), so
  you get real code-completion and type-checking.
- `BASE_DIR` replaces Laravel's `base_path()`. `Path(__file__).resolve().parent.parent`
  walks up from config/settings.py to the project root, just like `base_path()`.
"""
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()  # read .env — similar to Laravel's env() helper

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY: in production ALWAYS set SECRET_KEY via env. The fallback below is
# dev-only and must never reach production (like Laravel's APP_KEY).
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-dev-only-change-me")
DEBUG = os.getenv("DEBUG", "True") == "True"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")

# ---------------------------------------------------------------------------
# APPLICATIONS
# `INSTALLED_APPS` is Django's service-provider list. Django's own "core"
# apps (admin, auth, sessions...) are first, then OUR business apps.
# Adding an app here is like registering a Laravel ServiceProvider.
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",  # like Laravel's polymorphic types / schema cache
    "django.contrib.sessions",
    "django.contrib.messages",      # flash messages — exactly like Laravel's session()->flash()
    "django.contrib.staticfiles",   # asset pipeline — like Laravel's mix()/Vite helper
    # --- project apps (built feature-by-feature) ---
    "accounts",
    "dashboard",
    "categories",
    "units",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",            # CSRF — like Laravel's VerifyCsrfToken
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"  # routing entrypoint — like Laravel's routes/web.php

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # Global templates dir (our base.html). APP_DIRS=True also lets each
        # app keep its own templates/<app>/... folder (like Laravel's views per module).
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",  # exposes `user` in every template
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ---------------------------------------------------------------------------
# DATABASE
# Default: SQLite (zero install, perfect for learning & tests).
# Flip to PostgreSQL by setting DB_ENGINE=postgres in .env — no code change.
# This is the Django equivalent of swapping the connection in
# Laravel's config/database.php via DB_CONNECTION.
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

if os.getenv("DB_ENGINE") == "postgres":
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "warehouse"),
        "USER": os.getenv("DB_USER", "warehouse"),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }

# Tell Django which model is THE user model. Setting this early is a Django
# best-practice: if you swap it later, every migration breaks. Decide once.
AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Auth flow redirects
LOGIN_URL = "accounts:login"  # must be a named URL — like Laravel's route name
LOGIN_REDIRECT_URL = "dashboard:home"   # where to go after login
LOGOUT_REDIRECT_URL = "accounts:login"

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Jakarta"   # like Laravel's config('app.timezone')
USE_I18N = True
USE_TZ = True                # Django stores datetimes in UTC, like Laravel's 'timestamps'

# Static & media (uploads). MEDIA_ROOT is where Product images will live later.
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"  # used by `collectstatic` in production

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

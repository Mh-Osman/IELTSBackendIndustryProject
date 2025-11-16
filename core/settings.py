"""
Django settings for core project.
"""

from pathlib import Path
import os
import environ
from decouple import config
from datetime import timedelta

# ----------------------------------
# Base Directory
# ----------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ----------------------------------
# ENV Setup
# ----------------------------------
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")

ALLOWED_HOSTS = [
    "10.10.13.61",
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
]

# ----------------------------------
# Installed Apps
# ----------------------------------
INSTALLED_APPS = [
    "unfold",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Cloudinary
    "cloudinary_storage",
    "cloudinary",

    # Apps
    "users",
    "users_auth",
    "rest_framework",
    "rest_framework_simplejwt",
    "temp",
    "writing",
    "reading",

    # WebSocket
    "channels",
]

# ----------------------------------
# DRF + JWT
# ----------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=14),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
}

# ----------------------------------
# Middleware
# ----------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"
ASGI_APPLICATION = "core.asgi.application"   # REQUIRED for WebSocket

# ----------------------------------
# Database
# ----------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST"),
        "PORT": config("DB_PORT", default="5432"),
    }
}

# ----------------------------------
# Redis Variables from .env
# ----------------------------------
REDIS_HOST = config("REDIS_HOST")
REDIS_PORT = config("REDIS_PORT")

REDIS_CACHE_DB = config("REDIS_CACHE_DB")
REDIS_CELERY_BROKER_DB = config("REDIS_CELERY_BROKER_DB")
REDIS_CELERY_RESULT_DB = config("REDIS_CELERY_RESULT_DB")
REDIS_CHANNEL_LAYER_DB = config("REDIS_CHANNEL_LAYER_DB")

# ----------------------------------
# Caching with Redis (DB=1)
# ----------------------------------
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CACHE_DB}",
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
    }
}

# ----------------------------------
# Celery Configuration
# ----------------------------------
CELERY_BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CELERY_BROKER_DB}"
CELERY_RESULT_BACKEND = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CELERY_RESULT_DB}"

CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"

# ----------------------------------
# Channels WebSocket with Redis (DB=4)
# ----------------------------------
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(REDIS_HOST, int(REDIS_PORT))],
            "db": int(REDIS_CHANNEL_LAYER_DB),
        },
    },
}

# ----------------------------------
# Static & Media
# ----------------------------------
STATIC_URL = "static/"
MEDIA_URL = "/media/"

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": env("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": env("CLOUDINARY_API_KEY"),
    "API_SECRET": env("CLOUDINARY_API_SECRET"),
}

DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

AUTH_USER_MODEL = "users.CustomUser"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Unfold Admin UI
UNFOLD = {
    "SITE_TITLE": "IELTS Admin",
    "SITE_HEADER": "IELTS Management System",
    "SITE_URL": "/admin/",
    "SHOW_LOGOUT_LINK": True,
    "COLLAPSIBLE_SIDEBAR": True,
    "SHOW_SIDE_NAV": True,
    "STYLES": {"primary": "#2563eb", "accent": "#f59e0b"},
    "APPEARANCE": {"theme": "auto", "switcher": True},
}

# globaly work on utc
USE_TZ = True
TIME_ZONE = "UTC"

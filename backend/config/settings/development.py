"""
Development settings for Real Estate Price Prediction backend.
"""
from .base import *  # noqa: F403
import os

DEBUG = True

ALLOWED_HOSTS = ['*']

# CORS settings for local Next.js frontend
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]

# Development database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # noqa: F405
    }
}

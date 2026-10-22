"""
Production settings placeholder for Real Estate Price Prediction backend.
"""
from .base import *  # noqa: F403
import os

DEBUG = False

# Must be explicitly configured via environment in production
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')
SECRET_KEY = os.environ.get('SECRET_KEY')

CORS_ALLOWED_ORIGINS = [
    origin.strip() for origin in os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',') if origin.strip()
]

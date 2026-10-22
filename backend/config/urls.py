"""
URL configuration for backend project.
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def health_check(request):
    """
    Health check endpoint returning service liveness.
    Does NOT claim ML model readiness.
    """
    return JsonResponse({
        "status": "ok",
        "service": "real-estate-backend",
        "version": "1.0.0-scaffold",
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/health/', health_check, name='api-health'),
    path('api/v1/auth/', include('apps.accounts.urls')),
    path('api/v1/locations/', include('apps.properties.urls')),
    path('api/v1/predictions/', include('apps.predictions.urls')),
    path('api/v1/admin/', include('apps.analytics.urls')),
]

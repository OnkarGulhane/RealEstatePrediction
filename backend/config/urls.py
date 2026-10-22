"""
URL configuration for backend project.
"""
from django.contrib import admin
from django.urls import path
from django.http import JsonResponse

def health_check(request):
    """
    Minimal scaffold health endpoint.
    Returns status ok and service identifier.
    Note: Does NOT claim ML model readiness.
    """
    return JsonResponse({
        "status": "ok",
        "service": "real-estate-backend",
        "version": "1.0.0-scaffold",
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/health/', health_check, name='api-health'),
]

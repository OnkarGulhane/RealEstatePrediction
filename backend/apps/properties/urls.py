from django.urls import path
from .views import LocationsMetadataView

urlpatterns = [
    path('', LocationsMetadataView.as_view(), name='locations-metadata'),
]

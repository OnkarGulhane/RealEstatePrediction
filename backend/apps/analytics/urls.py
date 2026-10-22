from django.urls import path
from .views import (
    AdminSummaryView,
    AdminUserListView,
    AdminPredictionListView,
    AdminReportsView,
    AdminModelMetadataView,
)

urlpatterns = [
    path('summary/', AdminSummaryView.as_view(), name='admin-summary'),
    path('users/', AdminUserListView.as_view(), name='admin-users'),
    path('predictions/', AdminPredictionListView.as_view(), name='admin-predictions'),
    path('reports/', AdminReportsView.as_view(), name='admin-reports'),
    path('model/', AdminModelMetadataView.as_view(), name='admin-model-metadata'),
]

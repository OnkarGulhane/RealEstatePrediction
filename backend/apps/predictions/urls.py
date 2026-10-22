from django.urls import path
from .views import PredictionListCreateView, PredictionDetailView

urlpatterns = [
    path('', PredictionListCreateView.as_view(), name='prediction-list-create'),
    path('<uuid:pk>/', PredictionDetailView.as_view(), name='prediction-detail'),
]

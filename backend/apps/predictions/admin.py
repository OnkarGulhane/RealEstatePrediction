from django.contrib import admin
from .models import Prediction


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "location", "area_value", "area_basis", "estimated_price_inr", "model_version", "created_at")
    list_filter = ("area_basis", "location", "model_version", "created_at")
    search_fields = ("user__email", "location", "request_id")
    readonly_fields = ("id", "created_at", "request_id")
    ordering = ("-created_at",)

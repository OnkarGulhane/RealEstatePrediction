import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class Prediction(models.Model):
    """
    Persisted record of a successful residential property price prediction.
    Only successful finite positive predictions are saved.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="predictions",
        db_index=True,
    )

    # Input snapshot
    location = models.CharField(max_length=150, db_index=True)
    area_value = models.FloatField()
    area_basis = models.CharField(max_length=20)  # 'CARPET' or 'SUPER'
    bhk = models.IntegerField(null=True, blank=True)
    bathrooms = models.FloatField(null=True, blank=True)
    balcony = models.IntegerField(null=True, blank=True)
    floor_number = models.FloatField(null=True, blank=True)
    total_floors = models.FloatField(null=True, blank=True)
    parking_spaces = models.IntegerField(null=True, blank=True)
    furnishing = models.CharField(max_length=100, null=True, blank=True)
    transaction_type = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True)
    facing = models.CharField(max_length=100, null=True, blank=True)
    ownership = models.CharField(max_length=100, null=True, blank=True)

    # Inference output & metadata
    estimated_price_inr = models.DecimalField(max_digits=16, decimal_places=2)
    currency = models.CharField(max_length=10, default="INR")
    model_version = models.CharField(max_length=100)
    schema_version = models.CharField(max_length=20, default="1.0")
    request_id = models.CharField(max_length=100, blank=True, db_index=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = "predictions_prediction"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["location", "-created_at"]),
        ]

    def __str__(self):
        return f"Prediction {self.id} — {self.location} (INR {self.estimated_price_inr})"

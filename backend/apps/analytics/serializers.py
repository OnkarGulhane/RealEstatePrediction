from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.predictions.models import Prediction

User = get_user_model()


class AdminUserSerializer(serializers.ModelSerializer):
    prediction_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "display_name",
            "is_staff",
            "is_active",
            "created_at",
            "prediction_count",
        ]
        read_only_fields = fields


class AdminPredictionSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Prediction
        fields = [
            "id",
            "user_id",
            "user_email",
            "location",
            "area_value",
            "area_basis",
            "bhk",
            "bathrooms",
            "balcony",
            "parking_spaces",
            "furnishing",
            "transaction_type",
            "status",
            "estimated_price_inr",
            "currency",
            "model_version",
            "schema_version",
            "request_id",
            "created_at",
        ]
        read_only_fields = fields

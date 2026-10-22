import json
import logging
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path
from decimal import Decimal

from django.conf import settings
from django.db.models import Count, Sum, Avg
from django.db.models.functions import TruncDate
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ValidationError

from apps.predictions.models import Prediction
from apps.predictions.clients.inference_client import InferenceClient, InferenceClientError
from .serializers import AdminUserSerializer, AdminPredictionSerializer
from apps.common.exceptions import get_request_id

User = get_user_model()
logger = logging.getLogger("backend.analytics")


class AdminPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class AdminSummaryView(APIView):
    """
    Administrator dashboard summary computed from live database records.
    """
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        now = timezone.now()
        yesterday = now - timedelta(hours=24)
        seven_days_ago = now - timedelta(days=7)

        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        staff_users = User.objects.filter(is_staff=True).count()

        pred_qs = Prediction.objects.all()
        total_predictions = pred_qs.count()
        aggregates = pred_qs.aggregate(
            total_val=Sum("estimated_price_inr"),
            avg_val=Avg("estimated_price_inr"),
        )
        total_volume = float(aggregates["total_val"] or 0.0)
        avg_price = float(aggregates["avg_val"] or 0.0)

        preds_24h = pred_qs.filter(created_at__gte=yesterday).count()
        preds_7d = pred_qs.filter(created_at__gte=seven_days_ago).count()

        return Response({
            "users": {
                "total": total_users,
                "active": active_users,
                "staff": staff_users,
            },
            "predictions": {
                "total": total_predictions,
                "total_volume_inr": round(total_volume, 2),
                "average_price_inr": round(avg_price, 2),
                "last_24_hours": preds_24h,
                "last_7_days": preds_7d,
            },
            "currency": "INR",
            "server_time": now.isoformat(),
        })


class AdminUserListView(APIView):
    """
    Paginated administrator listing of registered users with safe allowlisted fields.
    """
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        paginator = AdminPagination()
        qs = User.objects.annotate(prediction_count=Count("predictions")).order_by("-created_at")

        search = request.query_params.get("search", "").strip()
        if search:
            qs = qs.filter(email__icontains=search) | qs.filter(display_name__icontains=search)

        page = paginator.paginate_queryset(qs, request)
        serializer = AdminUserSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class AdminPredictionListView(APIView):
    """
    Paginated administrator listing of all property prediction records across users.
    """
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        paginator = AdminPagination()
        qs = Prediction.objects.select_related("user").order_by("-created_at")

        location = request.query_params.get("location", "").strip()
        if location:
            qs = qs.filter(location__iexact=location)

        area_basis = request.query_params.get("area_basis", "").strip().upper()
        if area_basis in ("CARPET", "SUPER"):
            qs = qs.filter(area_basis=area_basis)

        user_id = request.query_params.get("user_id", "").strip()
        if user_id:
            qs = qs.filter(user_id=user_id)

        page = paginator.paginate_queryset(qs, request)
        serializer = AdminPredictionSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class AdminReportsView(APIView):
    """
    Date-filtered prediction volume and value reports with timezone boundary validation.
    """
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        tz_str = getattr(settings, "TIME_ZONE", "Asia/Kolkata")
        local_tz = ZoneInfo(tz_str)

        start_str = request.query_params.get("start_date")
        end_str = request.query_params.get("end_date")

        now_local = timezone.now().astimezone(local_tz)

        if not start_str:
            start_date = (now_local - timedelta(days=30)).date()
        else:
            try:
                start_date = datetime.strptime(start_str.strip(), "%Y-%m-%d").date()
            except ValueError:
                raise ValidationError({"start_date": "Format must be YYYY-MM-DD."})

        if not end_str:
            end_date = now_local.date()
        else:
            try:
                end_date = datetime.strptime(end_str.strip(), "%Y-%m-%d").date()
            except ValueError:
                raise ValidationError({"end_date": "Format must be YYYY-MM-DD."})

        if start_date > end_date:
            raise ValidationError({"start_date": "start_date cannot be later than end_date."})

        # Calculate exact start of start_date and end of end_date in local timezone
        start_dt = datetime.combine(start_date, time.min, tzinfo=local_tz)
        end_dt = datetime.combine(end_date, time.max, tzinfo=local_tz)

        qs = Prediction.objects.filter(created_at__gte=start_dt, created_at__lte=end_dt)

        aggregates = qs.aggregate(
            total_count=Count("id"),
            total_val=Sum("estimated_price_inr"),
            avg_val=Avg("estimated_price_inr"),
        )
        total_count = aggregates["total_count"] or 0
        total_volume = float(aggregates["total_val"] or 0.0)
        avg_price = float(aggregates["avg_val"] or 0.0)

        # Top locations in period
        top_locations = list(
            qs.values("location")
            .annotate(count=Count("id"), volume=Sum("estimated_price_inr"))
            .order_by("-count")[:5]
        )

        # Daily breakdown
        daily_records = list(
            qs.annotate(date=TruncDate("created_at", tzinfo=local_tz))
            .values("date")
            .annotate(count=Count("id"), volume=Sum("estimated_price_inr"))
            .order_by("date")
        )

        return Response({
            "period": {
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "timezone": tz_str,
            },
            "summary": {
                "total_predictions": total_count,
                "total_volume_inr": round(total_volume, 2),
                "average_price_inr": round(avg_price, 2),
            },
            "top_locations": [
                {
                    "location": item["location"],
                    "count": item["count"],
                    "volume_inr": round(float(item["volume"] or 0.0), 2),
                }
                for item in top_locations
            ],
            "daily": [
                {
                    "date": item["date"].strftime("%Y-%m-%d") if item["date"] else "",
                    "count": item["count"],
                    "volume_inr": round(float(item["volume"] or 0.0), 2),
                }
                for item in daily_records
            ],
        })


class AdminModelMetadataView(APIView):
    """
    Administrator-only view of published model metadata and evaluation metrics.
    """
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        request_id = get_request_id(request)
        client = InferenceClient()

        # Try live query from inference service first
        try:
            live_meta = client.get_model_metadata(request_id=request_id)
            return Response(live_meta, status=status.HTTP_200_OK)
        except Exception as e:
            logger.info("Inference service metadata endpoint unavailable (%s); falling back to canonical metadata summary.", e)

        # Fallback to local verified metadata summary without leaking system paths
        canonical_summary = {
            "model_id": "real_estate_hist_gradient_boosting_log_tuned_v1",
            "algorithm": "HistGradientBoostingRegressor (Tuned, log-target transform)",
            "target": {"unit": "INR", "currency": "INR"},
            "features": {"total_features": 22},
            "test_evaluation": {
                "holdout_mae_inr": 2693927.27,
                "holdout_rmse_inr": 8517820.69,
                "holdout_r2": 0.7104,
                "baseline_dummy_mae_inr": 6251646.75,
                "relative_mae_improvement": "56.91%",
            },
            "disclaimer": "Internal administrative view of offline model evaluation metrics.",
        }
        return Response(canonical_summary, status=status.HTTP_200_OK)

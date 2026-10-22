import logging
from decimal import Decimal
from django.http import Http404
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ValidationError

from .models import Prediction
from .serializers import PropertyPredictionInputSerializer, PredictionResponseSerializer
from .clients.inference_client import InferenceClient, InferenceClientError
from apps.common.exceptions import get_request_id

logger = logging.getLogger("backend.predictions")


class PredictionPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class PredictionListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        request_id = get_request_id(request)
        serializer = PropertyPredictionInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        valid_input = serializer.validated_data

        client = InferenceClient()
        try:
            inference_result = client.predict(valid_input, request_id=request_id)
        except InferenceClientError as e:
            logger.warning("Inference client error during prediction (req_id=%s): %s", request_id, e.message)
            return Response(
                {
                    "error": {
                        "code": e.code,
                        "message": e.message,
                        "fields": e.detail,
                        "request_id": request_id,
                    }
                },
                status=e.status_code,
            )

        # Extract returned price and metadata
        price_val = inference_result.get("estimated_price_inr")
        if price_val is None or price_val <= 0:
            logger.error("Inference service returned invalid non-positive price: %s", price_val)
            return Response(
                {
                    "error": {
                        "code": "INVALID_MODEL_OUTPUT",
                        "message": "Inference service returned an invalid price estimate.",
                        "fields": {},
                        "request_id": request_id,
                    }
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Save successful prediction to database
        prediction = Prediction.objects.create(
            user=request.user,
            location=valid_input["location"],
            area_value=valid_input["area_value"],
            area_basis=valid_input["area_basis"],
            bhk=valid_input.get("bhk"),
            bathrooms=valid_input.get("bathrooms"),
            balcony=valid_input.get("balcony"),
            floor_number=valid_input.get("floor_number"),
            total_floors=valid_input.get("total_floors"),
            parking_spaces=valid_input.get("parking_spaces"),
            furnishing=valid_input.get("furnishing"),
            transaction_type=valid_input.get("transaction_type"),
            status=valid_input.get("status"),
            facing=valid_input.get("facing"),
            ownership=valid_input.get("ownership"),
            estimated_price_inr=Decimal(str(round(float(price_val), 2))),
            currency=inference_result.get("currency", "INR"),
            model_version=inference_result.get("model_version", "unknown"),
            schema_version=valid_input.get("schema_version", "1.0"),
            request_id=request_id,
        )

        logger.info("Saved prediction %s for user %s (req_id=%s)", prediction.id, request.user.email, request_id)
        out_serializer = PredictionResponseSerializer(prediction)
        return Response(out_serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request):
        paginator = PredictionPagination()
        qs = Prediction.objects.filter(user=request.user).order_by("-created_at")
        page = paginator.paginate_queryset(qs, request)
        serializer = PredictionResponseSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class PredictionDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            prediction = Prediction.objects.get(pk=pk)
        except (Prediction.DoesNotExist, ValueError):
            raise Http404("Prediction not found.")

        # Strict object-level ownership check
        if prediction.user != request.user and not request.user.is_staff:
            raise Http404("Prediction not found.")

        serializer = PredictionResponseSerializer(prediction)
        return Response(serializer.data, status=status.HTTP_200_OK)

from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "display_name", "is_staff", "is_active", "created_at"]
        read_only_fields = ["id", "email", "is_staff", "is_active", "created_at"]


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["display_name"]

    def validate_display_name(self, value: str) -> str:
        return value.strip()


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(write_only=True, min_length=8)
    display_name = serializers.CharField(max_length=150, required=False, allow_blank=True, default="")

    def validate_email(self, value: str) -> str:
        norm_email = value.strip().lower()
        if User.objects.filter(email__iexact=norm_email).exists():
            raise serializers.ValidationError("A user with this email address already exists.")
        return norm_email

    def validate_password(self, value: str) -> str:
        validate_password(value)
        return value

    def create(self, validated_data: dict) -> User:
        # Strictly create normal user; ignore any privileged attributes
        return User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            display_name=validated_data.get("display_name", ""),
            is_staff=False,
            is_superuser=False,
        )


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs: dict) -> dict:
        email = attrs.get("email", "").strip().lower()
        password = attrs.get("password", "")

        user = authenticate(username=email, password=password)
        if not user:
            # Also try direct email match in case backend user lookup difference
            try:
                candidate = User.objects.get(email__iexact=email)
                if candidate.check_password(password):
                    user = candidate
            except User.DoesNotExist:
                pass

        if not user or not user.is_active:
            raise serializers.ValidationError("Invalid email address or password.")

        refresh = RefreshToken.for_user(user)
        return {
            "user": user,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

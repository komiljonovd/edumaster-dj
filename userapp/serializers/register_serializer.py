from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "gender",
            "birth_date",
            "address",
            "password",
            "password_confirm",
            "role",
        )

    def validate(self, attrs: dict) -> dict:
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password": "The passwords did not match."}
            )

        if attrs.get("role") in ["SUPER_ADMIN", "ADMIN"]:
            raise serializers.ValidationError(
                {"role": "You do not have the right to create such a role."}
            )

        return attrs

    def validate_first_name(self, value: str) -> str:
        cleaned_value = value.strip()
        if not cleaned_value:
            raise serializers.ValidationError("The name cannot be empty.")
        return cleaned_value

    def validate_last_name(self, value: str) -> str:
        cleaned_value = value.strip()
        if not cleaned_value:
            raise serializers.ValidationError("The last name cannot be empty.")
        return cleaned_value

    def validate_birth_date(self, value):
        if value and value > timezone.now().date():
            raise serializers.ValidationError(
                "The date of birth cannot be in the future."
            )
        return value

    def create(self, validated_data: dict):
        validated_data.pop("password_confirm")
        user = User.objects.create_user(**validated_data)
        return user

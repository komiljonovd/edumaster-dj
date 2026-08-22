from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "address",
            "birth_date",
            "gender",
        ]

        read_only_fields = ["id", "email"]

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

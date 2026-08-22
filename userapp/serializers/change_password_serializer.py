from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(
        required=True, validators=[validate_password], write_only=True
    )
    new_password_confirm = serializers.CharField(required=True, write_only=True)

    def validate_old_password(self, value: str) -> str:
        request = self.context.get("request")
        if request and not request.user.check_password(value):
            raise serializers.ValidationError(
                "The old password was entered incorrectly."
            )
        return value

    def validate(self, attrs: dict) -> dict:
        old_pass = attrs.get("old_password")
        new_pass = attrs.get("new_password")
        confirm_pass = attrs.get("new_password_confirm")

        if new_pass != confirm_pass:
            raise serializers.ValidationError(
                {"new_password_confirm": "The new passwords do not match."}
            )

        if old_pass == new_pass:
            raise serializers.ValidationError(
                {"new_password": "The new password must not match the old one."}
            )

        return attrs

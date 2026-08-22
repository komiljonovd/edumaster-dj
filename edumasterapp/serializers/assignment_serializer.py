from rest_framework import serializers
from ..models import Assignment
from django.utils import timezone


class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ["id", "lesson", "title", "description", "deadline", "max_score"]

    def validate_title(self, value: str) -> str:
        cleaned_title = value.strip()
        if len(cleaned_title) < 3:
            raise serializers.ValidationError(
                "The task title must contain at least 3 characters."
            )
        return cleaned_title

    def validate_deadline(self, value) -> timezone.datetime:
        if value <= timezone.now():
            raise serializers.ValidationError(
                "The Assignment deadline cannot be in the past."
            )
        return value

    def validate_max_score(self, value: int) -> int:
        if value <= 0:
            raise serializers.ValidationError(
                "The maximum score must be greater than zero."
            )
        return value

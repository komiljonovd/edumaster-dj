from rest_framework import serializers
from ..models import Lesson


class LessonSerializer(serializers.ModelSerializer):
    course_title = serializers.ReadOnlyField(source="course.title")

    class Meta:
        model = Lesson
        fields = [
            "id",
            "course",
            "course_title",
            "description",
            "title",
            "video",
            "pdf",
            "order",
            "duration",
        ]

    def validate_order(self, value: int) -> int:
        if value < 1:
            raise serializers.ValidationError(
                "The lesson order number cannot be less than 1."
            )
        return value

    def validate_video(self, value):
        if not value:
            return value

        file_name = getattr(value, "name", str(value)).lower()

        valid_extensions = [".mp4", ".avi", ".mov", ".mkv", ".webm"]
        if not any(file_name.endswith(ext) for ext in valid_extensions):
            raise serializers.ValidationError(
                "Invalid video format. Allowed: MP4, MOV, AVI, MKV, WEBM."
            )
        return value

    def validate_pdf(self, value):
        if not value:
            return value

        file_name = getattr(value, "name", str(value)).lower()

        if not file_name.endswith(".pdf"):
            raise serializers.ValidationError(
                "The lesson document must be in PDF format."
            )
        return value

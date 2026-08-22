from rest_framework import serializers
from ..models import Quiz


class QuizSerializer(serializers.ModelSerializer):
    course_name = serializers.ReadOnlyField(source="course.title")

    class Meta:
        model = Quiz
        fields = [
            "id",
            "course",
            "course_name",
            "title",
            "description",
            "time_limit_mins",
            "attempts_count",
            "min_score",
            "max_score",
            "total_questions",
        ]

    def validate_title(self, value: str) -> str:
        cleaned_title = value.strip()
        if len(cleaned_title) < 3:
            raise serializers.ValidationError(
                "The quiz name must contain at least 3 characters.."
            )
        return cleaned_title

    def validate_time_limit_mins(self, value: int) -> int:
        if value <= 0:
            raise serializers.ValidationError(
                "The time limit must be at least 1 minute."
            )
        if value > 180:
            raise serializers.ValidationError(
                "The time limit cannot exceed 180 minutes."
            )
        return value

    def validate_attempts_count(self, value: int) -> int:
        if value < 1:
            raise serializers.ValidationError(
                "The number of attempts must be at least 1."
            )
        return value

    def validate_min_score(self, value: int) -> int:
        if value < 0:
            raise serializers.ValidationError(
                "The minimum (passing) score cannot be negative."
            )
        return value

    def validate_max_score(self, value: int) -> int:
        if value <= 0:
            raise serializers.ValidationError(
                "The maximum score for the test must be greater than 0."
            )
        return value

    def validate(self, attrs: dict) -> dict:

        min_score = attrs.get(
            "min_score", self.instance.min_score if self.instance else None
        )
        max_score = attrs.get(
            "max_score", self.instance.max_score if self.instance else None
        )

        if min_score is not None and max_score is not None:
            if min_score >= max_score:
                raise serializers.ValidationError(
                    {
                        "min_score": (
                            f"The passing score ({min_score}) cannot exceed "
                            f"or equal the maximum test score ({max_score})."
                        )
                    }
                )

        return attrs

from rest_framework import serializers
from ..models import Question


class QuestionSerializer(serializers.ModelSerializer):
    correct_answer = serializers.CharField(write_only=True)

    class Meta:
        model = Question
        fields = [
            "id",
            "quiz",
            "text",
            "marks",
            "option1",
            "option2",
            "option3",
            "option4",
            "correct_answer",
        ]

    def validate_marks(self, value: int) -> int:
        if value <= 0:
            raise serializers.ValidationError(
                "The score for the question must be greater than zero."
            )
        return value

    def validate_text(self, value: str) -> str:
        cleaned_value = value.strip()
        if not cleaned_value:
            raise serializers.ValidationError("The question text cannot be empty.")
        return cleaned_value

    def validate(self, attrs: dict) -> dict:
        option1 = attrs.get("option1")
        option2 = attrs.get("option2")
        option3 = attrs.get("option3")
        option4 = attrs.get("option4")
        correct = attrs.get("correct_answer")

        options_dict = {
            "option1": option1,
            "option2": option2,
            "option3": option3,
            "option4": option4,
        }

        for key, text in options_dict.items():
            if text and not text.strip():
                raise serializers.ValidationError(
                    {key: "The answer option cannot be empty."}
                )

            mapping = {
                "option1": option1,
                "option2": option2,
                "option3": option3,
                "option4": option4,
            }

            if correct in mapping and not mapping[correct]:
                raise serializers.ValidationError(
                    {
                        "correct_answer": (
                            f"You selected {correct} as the correct answer, but this option is empty."
                        )
                    }
                )

            return attrs

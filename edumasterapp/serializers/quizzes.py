from rest_framework import serializers
from ..models import Quiz, Question, QuizAttempt


class QuizDetailSerializer(serializers.ModelSerializer):
    """Основная информация о тесте для студента."""

    total_questions = serializers.IntegerField(read_only=True)

    class Meta:
        model = Quiz
        fields = (
            "id",
            "course",
            "title",
            "description",
            "time_limit_mins",
            "attempts_count",
            "min_score",
            "max_score",
            "total_questions",
        )


class QuestionStudentSerializer(serializers.ModelSerializer):
    """Вопрос теста без раскрытия correct_answer."""

    class Meta:
        model = Question
        fields = ("id", "text", "marks", "option1", "option2", "option3", "option4")


class QuizSubmitSerializer(serializers.Serializer):
    """Сериализатор входящего JSON с ответами студента."""

    answers = serializers.DictField(
        child=serializers.CharField(max_length=255),
        help_text='Формат: {"<question_id>": "option1", "<question_id>": "option3"}',
    )

    def validate_answers(self, value: dict) -> dict:
        if not value:
            raise serializers.ValidationError(
                "Вы не ответили ни на один вопрос. Отправьте хотя бы один ответ."
            )
        return value


class QuizAttemptResultSerializer(serializers.ModelSerializer):
    """Результат сдачи теста."""

    quiz_title = serializers.CharField(source="quiz.title", read_only=True)
    min_score = serializers.IntegerField(source="quiz.min_score", read_only=True)
    max_score = serializers.IntegerField(source="quiz.max_score", read_only=True)

    class Meta:
        model = QuizAttempt
        fields = (
            "id",
            "quiz_title",
            "score",
            "min_score",
            "max_score",
            "is_passed",
            "started_at",
            "completed_at",
        )

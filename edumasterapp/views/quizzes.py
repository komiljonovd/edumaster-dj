from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from ..permissions.global_permissions import IsStudentHasCreation
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..models import Quiz, QuizAttempt, Question
from ..serializers.quizzes import (
    QuizDetailSerializer,
    QuestionStudentSerializer,
    QuizSubmitSerializer,
    QuizAttemptResultSerializer,
)
from service.quiz.quizzes import QuizService
from ..permissions.paid_permissions import IsStudentHasQuiz


class QuizDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Get test details",
        operation_description="Returns basic information about the test (time limit, passing score, number of attempts) before it starts.",
        responses={200: QuizDetailSerializer},
        tags=["quiz-test"],
    )
    def get(self, request, quiz_id: int) -> Response:
        quiz = get_object_or_404(Quiz.objects.filter(is_deleted=False), id=quiz_id)
        serializer = QuizDetailSerializer(quiz)
        return Response(serializer.data, status=status.HTTP_200_OK)


class QuizStartAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsStudentHasQuiz]

    @swagger_auto_schema(
        operation_summary="Start the test (start the timer)",
        operation_description="Creates a test session in Redis, records the start time, and returns data for UI initialization. The timer begins counting from this point.",
        request_body=None,
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "quiz_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                    "title": openapi.Schema(type=openapi.TYPE_STRING),
                    "time_limit_mins": openapi.Schema(type=openapi.TYPE_INTEGER),
                    "min_score": openapi.Schema(type=openapi.TYPE_INTEGER),
                    "max_score": openapi.Schema(type=openapi.TYPE_INTEGER),
                    "remaining_attempts": openapi.Schema(type=openapi.TYPE_INTEGER),
                },
            ),
            400: "Превышен лимит попыток прохождения",
        },
        tags=["quiz-test"],
    )
    def post(self, request, quiz_id: int) -> Response:
        try:
            session_info = QuizService.start_quiz_session(
                student=request.user, quiz_id=quiz_id
            )
            return Response(session_info, status=status.HTTP_200_OK)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class QuizQuestionsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Get a list of test questions",
        operation_description="Returns test questions without correct answers. Available only after calling the /start/ endpoint (if the timer is active).",
        responses={
            200: QuestionStudentSerializer(many=True),
            403: "The test has not started or time has expired.",
        },
        tags=["quiz-test"],
    )
    def get(self, request, quiz_id: int) -> Response:
        cache_key = f"quiz_session:{request.user.id}:{quiz_id}"
        if not cache.get(cache_key):
            return Response(
                {
                    "error": "The test has not started or timed out. Call POST /start/ first."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        quiz = get_object_or_404(
            Quiz.objects.filter(is_deleted=False).prefetch_related("questions"),
            id=quiz_id,
        )
        active_questions = quiz.questions.filter(is_deleted=False)
        serializer = QuestionStudentSerializer(active_questions, many=True)

        return Response(
            {
                "quiz_id": quiz.id,
                "title": quiz.title,
                "time_limit_mins": quiz.time_limit_mins,
                "questions": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class QuizSubmitAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Take the test and get the results",
        operation_description="Принимает JSON с ответами студента. Высчитывает баллы, сравнивает с min_score, проверяет дедлайн по Redis и сохраняет попытку.",
        request_body=QuizSubmitSerializer,
        responses={
            201: QuizAttemptResultSerializer,
            400: "Validation error, session not found or timed out",
        },
        tags=["quiz-test"],
    )
    def post(self, request, quiz_id: int) -> Response:
        serializer = QuizSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            attempt = QuizService.submit_and_evaluate(
                student=request.user,
                quiz_id=quiz_id,
                submitted_answers=serializer.validated_data["answers"],
            )
            result_data = QuizAttemptResultSerializer(attempt).data
            return Response(result_data, status=status.HTTP_201_CREATED)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class QuizAttemptHistoryAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="History of test attempts",
        operation_description="Provides a history of all attempts to pass a specific test by the currently logged in student.",
        responses={200: QuizAttemptResultSerializer(many=True)},
        tags=["quiz-test"],
    )
    def get(self, request, quiz_id: int) -> Response:
        attempts = (
            QuizAttempt.objects.filter(student=request.user, quiz_id=quiz_id)
            .select_related("quiz")
            .order_by("-started_at")
        )

        serializer = QuizAttemptResultSerializer(attempts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

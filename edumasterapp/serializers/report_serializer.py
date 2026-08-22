from django.utils import timezone
from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import Course, QuizAttempt, Certificate, Assignment, AssignmentSubmission

User = get_user_model()


class ChildQuizReportSerializer(serializers.ModelSerializer):
    """Результаты квизов ребенка."""

    quiz_title = serializers.CharField(source="quiz.title", read_only=True)
    course_title = serializers.CharField(
        source="quiz.lesson.course.title", read_only=True
    )

    class Meta:
        model = QuizAttempt
        fields = ("id", "quiz_title", "course_title", "score", "is_passed")


class ChildCertificateReportSerializer(serializers.ModelSerializer):
    """Сертификаты ребенка."""

    course_title = serializers.CharField(source="course.title", read_only=True)

    class Meta:
        model = Certificate
        fields = ("id", "course_title", "certificate_number", "issue_date")


class ChildAssignmentReportSerializer(serializers.ModelSerializer):
    """Дедлайны заданий и результаты сдачи ребенка."""

    lesson_title = serializers.CharField(source="lesson.title", read_only=True)
    course_title = serializers.CharField(source="lesson.course.title", read_only=True)
    is_overdue = serializers.SerializerMethodField()
    submission_status = serializers.SerializerMethodField()
    score = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = (
            "id",
            "title",
            "course_title",
            "lesson_title",
            "deadline",
            "is_overdue",
            "submission_status",
            "score",
        )

    def get_is_overdue(self, obj: Assignment) -> bool:
        return timezone.now() > obj.deadline

    def get_submission_status(self, obj: Assignment) -> str:
        student = self.context.get("student")
        submission = obj.submissions.filter(student=student, is_deleted=False).first()
        if not submission:
            return "not_submitted"
        return "graded" if submission.is_graded else "pending_review"

    def get_score(self, obj: Assignment) -> int | None:
        student = self.context.get("student")
        submission = obj.submissions.filter(student=student, is_deleted=False).first()
        return submission.score if submission else None


class ChildDetailReportSerializer(serializers.ModelSerializer):
    """Полный профиль ребенка с курсами, тестами, дедлайнами и сертификатами."""

    purchased_courses = serializers.SerializerMethodField()
    quizzes = serializers.SerializerMethodField()
    certificates = serializers.SerializerMethodField()
    assignments = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "purchased_courses",
            "quizzes",
            "assignments",
            "certificates",
        )

    def get_purchased_courses(self, student):
        paid_course_ids = student.payments.filter(status="completed").values_list(
            "course_id", flat=True
        )
        courses = Course.objects.filter(id__in=paid_course_ids, is_deleted=False)
        return [{"id": c.id, "title": c.title, "level": c.level} for c in courses]

    def get_quizzes(self, student):
        attempts = (
            QuizAttempt.objects.filter(student=student, is_deleted=False)
            .select_related("quiz", "quiz__course")
            .order_by("-completed_at")
        )
        return ChildQuizReportSerializer(attempts, many=True).data

    def get_certificates(self, student):
        certs = Certificate.objects.filter(
            student=student, is_deleted=False
        ).select_related("course")
        return ChildCertificateReportSerializer(certs, many=True).data

    def get_assignments(self, student):
        paid_course_ids = student.payments.filter(status="completed").values_list(
            "course_id", flat=True
        )
        assignments = (
            Assignment.objects.filter(
                lesson__course_id__in=paid_course_ids, is_deleted=False
            )
            .select_related("lesson", "lesson__course")
            .prefetch_related("submissions")
            .order_by("deadline")
        )
        return ChildAssignmentReportSerializer(
            assignments, many=True, context={"student": student}
        ).data

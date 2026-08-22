from django.contrib import admin, messages
from unfold.admin import ModelAdmin
from unfold.decorators import action, display
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.db.models import QuerySet
from django.http import HttpRequest
from django.core.cache import cache

from .models import (
    Course,
    Lesson,
    Category,
    Assignment,
    AssignmentSubmission,
    Quiz,
    Question,
    QuizAttempt,
    Payment,
    Certificate,
)

# Register your models here.


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ["id", "name", "created_at", "updated_at"]
    list_display_links = ["id", "name", "created_at", "updated_at"]
    search_fields = ["name"]
    list_filter = ["created_at", "updated_at"]
    ordering = ["-created_at"]


@admin.register(Course)
class CourseAdmin(ModelAdmin):
    list_display = [
        "id",
        "headshot_image",
        "title",
        "description",
        "category",
        "show_level",
        "price",
        "show_status",
        "duration",
        "total_lessons",
        "is_deleted",
        "author",
        "created_at",
        "updated_at",
    ]
    list_display_links = [
        "id",
        "headshot_image",
        "title",
        "description",
        "category",
        "show_level",
        "price",
        "show_status",
        "duration",
        "is_deleted",
        "author",
        "created_at",
        "updated_at",
    ]

    search_fields = ["title", "description", "category__name"]
    list_filter = ["created_at", "updated_at", "level", "status", "is_deleted"]
    autocomplete_fields = ["category"]
    actions = [
        "level_beginner",
        "level_intermediate",
        "level_advanced",
        "status_active",
        "status_inactive",
        "publish_course",
        "unpublish_course",
    ]
    list_per_page = 50

    @action(description="Course level assign as BEGINNER")
    def level_beginner(self, request: HttpRequest, queryset: QuerySet):
        course = queryset.exclude(level="BEGINNER")
        count = course.update(level="BEGINNER")

        cache.delete_pattern("*CourseListCreateAPI*")
        cache.delete_pattern("*CourseDetailApi*")

        if count:
            self.message_user(
                request, f"Successfully updated:{count}", messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                "There are no BEGINNER level courses in selected.",
                messages.WARNING,
            )

    @action(description="Course level assign as INTERMEDIATE")
    def level_intermediate(self, request: HttpRequest, queryset: QuerySet):
        course = queryset.exclude(level="INTERMEDIATE")
        count = course.update(level="INTERMEDIATE")

        cache.delete_pattern("*CourseListCreateAPI*")
        cache.delete_pattern("*CourseDetailApi*")

        if count:
            self.message_user(
                request, f"Successfully updated:{count}", messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                "There are no INTERMEDIATE level courses in selected.",
                messages.WARNING,
            )

    @action(description="Course level assign as ADVANCED")
    def level_advanced(self, request: HttpRequest, queryset: QuerySet):
        course = queryset.exclude(level="ADVANCED")
        count = course.update(level="ADVANCED")

        cache.delete_pattern("*CourseListCreateAPI*")
        cache.delete_pattern("*CourseDetailApi*")

        if count:
            self.message_user(
                request, f"Successfully updated:{count}", messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                "There are no ADVANCED level courses in selected.",
                messages.WARNING,
            )

    @action(description="Course status assign as ACTIVE")
    def status_active(self, request: HttpRequest, queryset: QuerySet):
        course = queryset.exclude(status="ACTIVE")
        count = course.update(status="ACTIVE")

        cache.delete_pattern("*CourseListCreateAPI*")
        cache.delete_pattern("*CourseDetailApi*")

        if count:
            self.message_user(
                request, f"Successfully updated:{count}", messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                "There are no INACTIVE status courses in selected.",
                messages.WARNING,
            )

    @action(description="Course status assign as INACTIVE")
    def status_inactive(self, request: HttpRequest, queryset: QuerySet):
        course = queryset.exclude(status="INACTIVE")
        count = course.update(status="INACTIVE")

        cache.delete_pattern("*CourseListCreateAPI*")
        cache.delete_pattern("*CourseDetailApi*")

        if count:
            self.message_user(
                request, f"Successfully updated:{count}", messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                "There are no ACTIVE status courses in selected.",
                messages.WARNING,
            )

    @action(description="Publish a Course")
    def publish_course(self, request: HttpRequest, queryset: QuerySet):
        course = queryset.exclude(is_deleted=False)
        count = course.update(is_deleted=False)

        cache.delete_pattern("*CourseListCreateAPI*")
        cache.delete_pattern("*CourseDetailApi*")

        if count:
            self.message_user(
                request, f"Successfully updated:{count}", messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                "There are no UNPUBLISHED courses in selected.",
                messages.WARNING,
            )

    @action(description="Unpublish a Course")
    def unpublish_course(self, request: HttpRequest, queryset: QuerySet):
        course = queryset.exclude(is_deleted=True)
        count = course.update(is_deleted=True)

        cache.delete_pattern("*CourseListCreateAPI*")
        cache.delete_pattern("*CourseDetailApi*")

        if count:
            self.message_user(
                request, f"Successfully updated:{count}", messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                "There are no PUBLISHED courses in selected.",
                messages.WARNING,
            )

    @display(
        description="Status",
        ordering="status",
        label={"ACTIVE": "success", "INACTIVE": "danger"},
    )
    def show_status(self, obj):
        return obj.get_status_display()

    @display(
        description="Level",
        ordering="level",
        label={"BEGINNER": "default", "INTERMEDIATE": "info", "ADVANCED": "warning"},
    )
    def show_level(self, obj):
        return obj.get_level_display()

    def headshot_image(self, obj):
        return mark_safe(
            '<img src="{url}" width="100" height=100/>'.format(
                url=obj.image.url,
            )
        )

    headshot_image.short_description = "Image"


@admin.register(Lesson)
class LessonAdmin(ModelAdmin):
    list_display = [
        "id",
        "video_preview",
        "course",
        "title",
        "description",
        "order",
        "duration",
        "is_deleted",
        "created_at",
        "updated_at",
    ]
    list_display_links = [
        "id",
        "video_preview",
        "course",
        "title",
        "description",
        "order",
        "duration",
        "is_deleted",
        "created_at",
        "updated_at",
    ]
    search_fields = ["course__title", "title", "description"]
    list_filter = ["created_at", "updated_at", "is_deleted"]
    autocomplete_fields = ["course"]
    actions = ["publish_lesson", "unpublish_lesson"]
    list_per_page = 50

    def video_preview(self, obj):
        if obj.video:
            return format_html(
                '<video width="150" height="150" controls>'
                '<source src="{}" type="video/mp4">'
                "Your browser does not support the video tag."
                "</video>",
                obj.video.url,
            )
        return "No video uploaded"

    # Change the column header name in admin
    video_preview.short_description = "Video"

    @action(description="Publish a Lesson")
    def publish_lesson(self, request: HttpRequest, queryset: QuerySet):
        lesson = queryset.exclude(is_deleted=False)
        count = lesson.update(is_deleted=False)
        cache.delete_pattern("*LessonDetailAPI*")

        if count:
            self.message_user(
                request, f"Successfully updated:{count}", messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                "There are no UNPUBLISHED lessons in selected.",
                messages.WARNING,
            )

    @action(description="Unpublish a Lesson")
    def unpublish_lesson(self, request: HttpRequest, queryset: QuerySet):
        lesson = queryset.exclude(is_deleted=True)
        count = lesson.update(is_deleted=True)
        cache.delete_pattern("*LessonDetailAPI*")

        if count:
            self.message_user(
                request, f"Successfully updated:{count}", messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                "There are no PUBLISHED lessons in selected.",
                messages.WARNING,
            )


@admin.register(Assignment)
class AssignmentAdmin(ModelAdmin):
    list_display = [
        "id",
        "lesson",
        "title",
        "description",
        "deadline",
        "max_score",
        "is_deleted",
        "created_at",
        "updated_at",
    ]
    list_display_links = [
        "id",
        "lesson",
        "title",
        "description",
        "deadline",
        "max_score",
        "is_deleted",
        "created_at",
        "updated_at",
    ]
    search_fields = ["lesson__title", "title", "description", "max_score"]
    ordering = ["-created_at"]
    list_filter = ["is_deleted", "created_at", "updated_at"]
    actions = ["remove_assignment", "restore_assignment"]

    @action(description="Remove ASSIGNMENT")
    def remove_assignment(self, request: HttpRequest, queryset: QuerySet):
        assignment = queryset.exclude(is_deleted=True)
        count = assignment.update(is_deleted=True)
        cache.delete_pattern("*AssignmentDetailAPI*")
        cache.delete_pattern("*AssignmentListCreateAPI*")
        cache.delete_pattern("*ParentChildrenReportAPIView*")
        if count:
            self.message_user(
                request, f"Successfully updated:{count}", messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                "No ASSIGNMENT(s) to remove.",
                messages.WARNING,
            )

    @action(description="Restore ASSIGNMENT")
    def restore_assignment(self, request: HttpRequest, queryset: QuerySet):
        assignment = queryset.exclude(is_deleted=False)
        count = assignment.update(is_deleted=False)
        cache.delete_pattern("*AssignmentDetailAPI*")
        cache.delete_pattern("*AssignmentListCreateAPI*")
        cache.delete_pattern("*ParentChildrenReportAPIView*")
        if count:
            self.message_user(
                request, f"Successfully updated:{count}", messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                "No ASSIGNMENT(s) to restore.",
                messages.WARNING,
            )


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(ModelAdmin):
    list_display = [
        "id",
        "assignment",
        "student",
        "file",
        "student_comment",
        "score",
        "teacher_comment",
        "is_graded",
        "is_deleted",
        "created_at",
        "updated_at",
    ]

    list_display_links = [
        "id",
        "assignment",
        "student",
        "file",
        "student_comment",
        "score",
        "teacher_comment",
        "is_graded",
        "is_deleted",
        "created_at",
        "updated_at",
    ]

    search_fields = ["student__email", "student_comment", "teacher_comment"]
    list_filter = [
        "is_graded",
        "is_deleted",
        "created_at",
        "updated_at",
    ]
    ordering = ["-created_at"]

    actions = ["restore_assignment_submission", "remove_assignment_submission"]

    @action(description="Remove ASSIGNMENT")
    def remove_assignment_submission(self, request: HttpRequest, queryset: QuerySet):
        assignment = queryset.exclude(is_deleted=True)
        count = assignment.update(is_deleted=True)
        cache.delete_pattern("*StudentCreateAssignmentAPI*")
        cache.delete_pattern("*ParentChildrenReportAPIView*")
        if count:
            self.message_user(
                request, f"Successfully updated:{count}", messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                "No ASSIGNMENT SUBMISSION(s) to remove.",
                messages.WARNING,
            )

    @action(description="Restore ASSIGNMENT")
    def restore_assignment_submission(self, request: HttpRequest, queryset: QuerySet):
        assignment = queryset.exclude(is_deleted=False)
        count = assignment.update(is_deleted=False)
        cache.delete_pattern("*StudentCreateAssignmentAPI*")
        cache.delete_pattern("*ParentChildrenReportAPIView*")
        if count:
            self.message_user(
                request, f"Successfully updated:{count}", messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                "No ASSIGNMENT SUBMISSION(s) to restore.",
                messages.WARNING,
            )


@admin.register(Quiz)
class QuizAdmin(ModelAdmin):
    list_display = [
        "id",
        "course",
        "title",
        "description",
        "time_limit_mins",
        "attempts_count",
        "total_questions",
        "is_deleted",
        "created_at",
        "updated_at",
    ]
    list_display_links = [
        "id",
        "course",
        "title",
        "description",
        "time_limit_mins",
        "attempts_count",
        "is_deleted",
        "created_at",
        "updated_at",
    ]
    search_fields = ["course__title", "title", "description"]
    ordering = ["-created_at"]
    list_filter = ["is_deleted", "created_at", "updated_at"]
    actions = ["remove_quiz", "restore_quiz"]

    @action(description="Remove QUIZ")
    def remove_quiz(self, request: HttpRequest, queryset: QuerySet):
        assignment = queryset.exclude(is_deleted=True)
        count = assignment.update(is_deleted=True)
        cache.delete_pattern("*QuizListCreateAPI*")
        cache.delete_pattern("*QuizDetailAPI*")
        cache.delete_pattern("*ParentChildrenReportAPIView*")

        if count:
            self.message_user(
                request, f"Successfully updated:{count}", messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                "No QUIZ(zes) to remove.",
                messages.WARNING,
            )

    @action(description="Restore QUIZ")
    def restore_quiz(self, request: HttpRequest, queryset: QuerySet):
        assignment = queryset.exclude(is_deleted=False)
        count = assignment.update(is_deleted=False)

        cache.delete_pattern("*QuizListCreateAPI*")
        cache.delete_pattern("*QuizDetailAPI*")
        cache.delete_pattern("*ParentChildrenReportAPIView*")

        if count:
            self.message_user(
                request, f"Successfully updated:{count}", messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                "No QUIZ(zes) to restore.",
                messages.WARNING,
            )


@admin.register(Question)
class QuestionAdmin(ModelAdmin):
    list_display = [
        "id",
        "quiz",
        "text",
        "marks",
        "option1",
        "option2",
        "option3",
        "option4",
        "correct_answer",
        "is_deleted",
        "created_at",
        "updated_at",
    ]
    list_display_links = [
        "id",
        "quiz",
        "text",
        "marks",
        "option1",
        "option2",
        "option3",
        "option4",
        "correct_answer",
        "is_deleted",
        "created_at",
        "updated_at",
    ]
    search_fields = ["quiz__title", "text", "option1", "option2", "option3", "option4"]
    ordering = ["-created_at"]
    list_filter = ["is_deleted", "created_at", "updated_at", "correct_answer"]
    actions = ["remove_quiz", "restore_quiz"]

    @action(description="Remove QUESTION")
    def remove_quiz(self, request: HttpRequest, queryset: QuerySet):
        question = queryset.exclude(is_deleted=True)
        count = question.update(is_deleted=True)
        cache.delete_pattern("*QuestionDetailAPI*")

        if count:
            self.message_user(
                request, f"Successfully updated:{count}", messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                "No QUESTION(s) to remove.",
                messages.WARNING,
            )

    @action(description="Restore QUESTION")
    def restore_quiz(self, request: HttpRequest, queryset: QuerySet):
        question = queryset.exclude(is_deleted=False)
        count = question.update(is_deleted=False)
        cache.delete_pattern("*QuestionDetailAPI*")

        if count:
            self.message_user(
                request, f"Successfully updated:{count}", messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                "No QUESTION(s) to restore.",
                messages.WARNING,
            )


@admin.register(QuizAttempt)
class QuizAttemptAdmin(ModelAdmin):
    list_display = [
        "id",
        "student",
        "quiz",
        "score",
        "is_passed",
        "is_deleted",
        "started_at",
        "completed_at",
    ]
    list_display_links = [
        "id",
        "student",
        "quiz",
        "score",
        "is_passed",
        "is_deleted",
        "is_completed",
        "started_at",
        "completed_at",
    ]
    search_fields = ["score", "student__email", "quiz__title"]
    ordering = ["-started_at"]
    list_filter = ["is_passed", "is_deleted", "started_at"]

    actions = ["remove_quiz_attempt", "restore_quiz_attempt"]

    @action(description="Remove QUIZ ATTEMPT")
    def remove_quiz_attempt(self, request: HttpRequest, queryset: QuerySet):
        quizzes = queryset.exclude(is_deleted=True)
        count = quizzes.update(is_deleted=True)
        cache.delete_pattern("*ParentChildrenReportAPIView*")

        if count:
            self.message_user(
                request, f"Successfully updated:{count}", messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                "No QUIZ ATTEMPT(s) to remove.",
                messages.WARNING,
            )

    @action(description="Restore QUIZ ATTEMPT")
    def restore_quiz_attempt(self, request: HttpRequest, queryset: QuerySet):
        quizzes = queryset.exclude(is_deleted=False)
        count = quizzes.update(is_deleted=False)
        cache.delete_pattern("*ParentChildrenReportAPIView*")

        if count:
            self.message_user(
                request, f"Successfully updated:{count}", messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                "No QUIZ ATTEMPT(s) to restore.",
                messages.WARNING,
            )


@admin.register(Payment)
class PaymentAdmin(ModelAdmin):
    list_display = [
        "id",
        "student",
        "course",
        "amount",
        "method",
        "status",
        "transaction_id",
        "payment_date",
        "is_deleted",
    ]
    list_display_links = [
        "id",
        "student",
        "course",
        "amount",
        "method",
        "status",
        "transaction_id",
        "payment_date",
        "is_deleted",
    ]
    search_fields = ["student__email", "student__role", "course__title"]
    ordering = ["-payment_date"]
    list_filter = ["is_deleted", "method", "status"]
    actions = ["remove_payment", "restore_payment"]

    @action(description="Remove PAYMENT")
    def remove_payment(self, request: HttpRequest, queryset: QuerySet):
        payment = queryset.exclude(is_deleted=True)
        count = payment.update(is_deleted=True)
        cache.delete_pattern("*PaymentListCreateAPI*")
        cache.delete_pattern("*PaymentDetailAPI*")
        if count:
            self.message_user(
                request, f"Successfully updated:{count}", messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                "No PAYMENT(s) to remove.",
                messages.WARNING,
            )

    @action(description="Restore PAYMENT")
    def restore_payment(self, request: HttpRequest, queryset: QuerySet):
        payment = queryset.exclude(is_deleted=False)
        count = payment.update(is_deleted=False)
        cache.delete_pattern("*PaymentListCreateAPI*")
        cache.delete_pattern("*PaymentDetailAPI*")
        if count:
            self.message_user(
                request, f"Successfully updated:{count}", messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                "No PAYMENT(s) to restore.",
                messages.WARNING,
            )


@admin.register(Certificate)
class CertificateAdmin(ModelAdmin):
    list_display = [
        "id",
        "show_image",
        "show_qr_code",
        "student",
        "course",
        "show_certificate_number",
        "is_deleted",
        "issue_date",
    ]
    list_display_links = [
        "id",
        "show_image",
        "show_qr_code",
        "student",
        "course",
        "show_certificate_number",
        "is_deleted",
        "issue_date",
    ]
    search_fields = [
        "student__email",
        "student__role",
        "course__title",
        "certificate_number",
    ]
    ordering = ["-issue_date"]
    list_filter = ["is_deleted"]
    actions = ["restore_certificate", "remove_certificate"]

    @action(description="Restore CERTIFICATE")
    def restore_certificate(self, request: HttpRequest, queryset: QuerySet):
        certificate = queryset.exclude(is_deleted=False)
        count = certificate.update(is_deleted=False)
        cache.delete_pattern("*CertificateListAPI*")
        cache.delete_pattern("*CertificateDetailAPI*")
        cache.delete_pattern("*ParentChildrenReportAPIView*")
        if count:
            self.message_user(
                request, f"Successfully updated:{count}", messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                "No CERTIFICATE(s) to restore.",
                messages.WARNING,
            )

    @action(description="Remove CERTIFICATE")
    def remove_certificate(self, request: HttpRequest, queryset: QuerySet):
        certificate = queryset.exclude(is_deleted=True)
        count = certificate.update(is_deleted=True)
        cache.delete_pattern("*CertificateListAPI*")
        cache.delete_pattern("*CertificateDetailAPI*")
        cache.delete_pattern("*ParentChildrenReportAPIView*")
        if count:
            self.message_user(
                request, f"Successfully updated:{count}", messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                "No CERTIFICATE(s) to remove.",
                messages.WARNING,
            )

    def show_image(self, obj):
        return mark_safe(
            '<img src="{url}" width="80" height=80/>'.format(
                url=obj.image.url,
            )
        )

    show_image.short_description = "Image"

    def show_qr_code(self, obj):
        return mark_safe(
            '<img src="{url}" width="60" height=60/>'.format(
                url=obj.qr_code.url,
            )
        )

    show_qr_code.short_description = "QR CODE"

    @display(
        description="Certificate Number", ordering="certificate_number", label=True
    )
    def show_certificate_number(self, obj):
        return obj.certificate_number

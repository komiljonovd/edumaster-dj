from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator
import uuid
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from core.storages import (
    PublicMediaStorage,
    PrivateDocumentStorage,
    PrivateVideoStorage,
)

# Create your models here.


User = get_user_model()


class Level(models.TextChoices):
    BEGINNER = "BEGINNER", _("BEGINNER")
    INTERMEDIATE = "INTERMEDIATE", _("INTERMEDIATE")
    ADVANCED = "ADVANCED", _("ADVANCED")


class Status(models.TextChoices):
    ACTIVE = "ACTIVE", _("ACTIVE")
    INACTIVE = "INACTIVE", _("INACTIVE")


class NonDeleted(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class SoftDelete(models.Model):
    is_deleted = models.BooleanField(default=False)
    everything = models.Manager()
    objects = NonDeleted()

    def delete(self):
        self.is_deleted = True
        self.save()

    def restore(self):
        self.is_deleted = False
        self.save()

    class Meta:
        abstract = True


class Category(models.Model):
    name = models.CharField(max_length=256, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "category"
        verbose_name = "category"
        verbose_name_plural = "categories"
        ordering = ["-created_at"]


class Course(SoftDelete):
    title = models.CharField(max_length=256, unique=True)
    description = models.CharField(max_length=256, db_index=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    level = models.CharField(choices=Level.choices, default=Level.INTERMEDIATE,max_length=20)
    price = models.DecimalField(max_digits=20, decimal_places=2, db_index=True)
    image = models.ImageField(
        upload_to="courses/images/",
        storage=PublicMediaStorage(),
        validators=[
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"])
        ],
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ACTIVE
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    duration = models.PositiveIntegerField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "course"
        verbose_name = "course"
        verbose_name_plural = "courses"
        ordering = ["-created_at"]

    @property
    def total_lessons(self) -> int:
        return self.lessons.count()


class Lesson(SoftDelete):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=255, db_index=True)
    video = models.FileField(
        upload_to="courses/videos/",
        storage=PrivateVideoStorage(),
        validators=[
            FileExtensionValidator(
                allowed_extensions=["mp4", "avi", "mov", "mkv", "webm"]
            )
        ],
    )
    pdf = models.FileField(
        upload_to="courses/pdfs/",
        storage=PrivateDocumentStorage(),
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
    )
    description = models.TextField(blank=True, db_index=True)
    order = models.PositiveIntegerField(db_index=True)
    duration = models.PositiveIntegerField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "lesson"
        verbose_name = "lesson"
        verbose_name_plural = "lessons"
        ordering = ["-created_at"]
        unique_together = ("course", "order")

    def __str__(self) -> str:
        return f"{self.course.title} - {self.title}"


class Assignment(SoftDelete):
    """Lesson assignment model for students."""

    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="assignments",
        help_text="Related lesson",
    )
    title = models.CharField(
        max_length=255, help_text="Assignment title", db_index=True
    )
    description = models.TextField(
        help_text="Detailed assignment description", db_index=True
    )
    deadline = models.DateTimeField(help_text="Submission deadline")
    max_score = models.PositiveIntegerField(
        default=100, help_text="Maximum possible score", db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.title} (Deadline: {self.deadline})"

    class Meta:
        db_table = "assignment"
        verbose_name = "assignment"
        verbose_name_plural = "assignments"
        ordering = ["-created_at"]


class AssignmentSubmission(SoftDelete):
    """Student submission for an assignment."""

    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name="submissions",
        help_text="Target assignment",
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="submissions",
        help_text="Student who submitted",
    )
    file = models.FileField(
        upload_to="assignments/submissions/",
        storage=PrivateDocumentStorage(),
        help_text="Uploaded submission file",
    )
    student_comment = models.TextField(
        blank=True, null=True, help_text="Comment from student", db_index=True
    )

    score = models.PositiveIntegerField(
        blank=True, null=True, help_text="Score given by teacher", db_index=True
    )
    teacher_comment = models.TextField(
        blank=True, null=True, help_text="Feedback from teacher", db_index=True
    )
    is_graded = models.BooleanField(default=False, help_text="Grading status")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Submission by {self.student.email} for {self.assignment.title}"

    class Meta:
        db_table = "assignmentsubmission"
        verbose_name = "assignmentsubmission"
        verbose_name_plural = "assignmentsubmissions"
        ordering = ["-created_at"]
        unique_together = ("assignment", "student")


# --- 5-MODUL: QUIZ ---
class Quiz(SoftDelete):
    """Course quiz model."""

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="quizzes",
        help_text="Related course",
    )
    title = models.CharField(max_length=255, help_text="Quiz name", db_index=True)
    description = models.TextField(
        blank=True, null=True, help_text="Quiz description", db_index=True
    )
    time_limit_mins = models.PositiveIntegerField(
        default=20, help_text="Time limit in minutes"
    )
    attempts_count = models.PositiveIntegerField(
        default=3, help_text="Allowed attempts count"
    )
    min_score = models.PositiveIntegerField(db_index=True)
    max_score = models.PositiveIntegerField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title

    @property
    def total_questions(self) -> int:
        return self.questions.count()

    class Meta:
        db_table = "quiz"
        verbose_name = "quiz"
        verbose_name_plural = "quiz"
        ordering = ["-created_at"]


class Question(SoftDelete):
    """Quiz question with 4 options and 1 correct answer."""

    class CorrectChoice(models.TextChoices):
        OPTION_1 = "option1", _("Option 1")
        OPTION_2 = "option2", _("Option 2")
        OPTION_3 = "option3", _("Option 3")
        OPTION_4 = "option4", _("Option 4")

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="questions",
        help_text="Parent quiz",
    )
    text = models.TextField(help_text="Question text", db_index=True)
    marks = models.PositiveIntegerField(
        default=1, help_text="Marks for this question", db_index=True
    )

    option1 = models.CharField(max_length=255, help_text="First option")
    option2 = models.CharField(max_length=255, help_text="Second option")
    option3 = models.CharField(max_length=255, help_text="Third option")
    option4 = models.CharField(max_length=255, help_text="Fourth option")

    correct_answer = models.CharField(
        max_length=10,
        choices=CorrectChoice.choices,
        help_text="Select the correct option",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Q: {self.text[:50]}"

    class Meta:
        db_table = "question"
        verbose_name = "question"
        verbose_name_plural = "questions"
        ordering = ["-created_at"]


class QuizAttempt(SoftDelete):
    """Student quiz attempt result storage."""

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="quiz_attempts",
        help_text="Student taking the quiz",
    )
    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE, related_name="attempts", help_text="Target quiz"
    )
    score = models.PositiveIntegerField(
        default=0, help_text="Total scored marks", db_index=True
    )
    is_passed = models.BooleanField(default=False, help_text="Passing status")
    started_at = models.DateTimeField(help_text="Время начала прохождения теста")
    completed_at = models.DateTimeField(
        null=True, blank=True, help_text="Время фактического завершения теста"
    )

    def __str__(self) -> str:
        status = "Passed" if self.is_passed else "Failed"
        return f"{self.student.email} - {self.quiz.title} ({status}: {self.score}%)"

    class Meta:
        db_table = "quizattempt"
        verbose_name = "quizattempt"
        verbose_name_plural = "quizattempts"
        ordering = ["-completed_at"]


# --- 6-MODUL: PAYMENT ---
class Payment(SoftDelete):
    """Course payment transaction model."""

    class PaymentMethod(models.TextChoices):
        CLICK = "click", "Click"
        PAYME = "payme", "Payme"
        UZUM = "uzum", "Uzum Bank"
        CARD = "card", "Bank Card"

    class PaymentStatus(models.TextChoices):
        PENDING = "pending", _("Pending")
        COMPLETED = "completed", _("Completed")
        FAILED = "failed", _("Failed")

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="payments",
        help_text="Student making the payment",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="payments",
        help_text="Target course",
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Payment amount"
    )
    method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        help_text="Payment gateway method",
        db_index=True,
    )
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        help_text="Transaction status",
        db_index=True,
    )
    transaction_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text="Unique certificate UUID",
    )
    payment_date = models.DateTimeField(
        blank=True, null=True, help_text="Successful payment timestamp"
    )

    def __str__(self) -> str:
        return f"Payment {self.transaction_id} - {self.status}"

    class Meta:
        db_table = "payment"
        verbose_name = "payment"
        verbose_name_plural = "payments"
        ordering = ["-payment_date"]


# --- 7-MODUL: CERTIFICATE ---
class Certificate(SoftDelete):
    """Automatic course completion certificate."""

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="certificates",
        help_text="Certificate owner",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="certificates",
        help_text="Completed course",
    )
    certificate_number = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text="Unique certificate UUID",
        db_index=True,
    )
    image = models.ImageField(
        upload_to="certificates/images/",
        storage=PublicMediaStorage(),
        null=True,
        blank=True,
        help_text="Изображение сертификата (PNG)",
    )
    qr_code = models.ImageField(
        upload_to="certificates/qrcodes/",
        storage=PublicMediaStorage(),
        blank=True,
        null=True,
        help_text="Verification QR code image",
    )
    issue_date = models.DateTimeField(auto_now_add=True, help_text="Date of issue")

    def __str__(self) -> str:
        return f"Certificate #{self.certificate_number} - {self.student.email}"

    class Meta:
        db_table = "certificate"
        verbose_name = "certificate"
        verbose_name_plural = "certificates"
        unique_together = ("student", "course")
        ordering = ["-issue_date"]

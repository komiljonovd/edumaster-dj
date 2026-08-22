from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from edumasterapp.models import Course, Assignment, AssignmentSubmission, Payment
from django.utils import timezone
from datetime import timedelta

# Предполагаем наличие моделей AssignmentSubmission, QuizAttempt, Certificate

User = get_user_model()


@shared_task(ignore_result=True)
def send_new_course_email_task(course_id: int) -> None:
    """Notification About New Course"""
    try:
        course = Course.objects.get(id=course_id)
        student_emails = list(
            User.objects.filter(role='STUDENT').values_list("email", flat=True)
        )

        if student_emails:
            send_mail(
                subject=f"New Course Available: {course.title}",
                message=f"Hello! A new course '{course.title}' has been added to EduMaster LMS. Check it out now!",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=student_emails,
                fail_silently=True,
            )
    except Course.DoesNotExist:
        pass


@shared_task
def notify_assignment_deadlines():
    now = timezone.now()

    for hours in (24, 3):
        assignments = Assignment.objects.filter(
            is_deleted=False,
            deadline__range=(
                now + timedelta(hours=hours - 0.25),
                now + timedelta(hours=hours),
            ),
        ).select_related("lesson__course")

        for a in assignments:
            students = (
                Payment.objects.filter(
                    course=a.lesson.course, status=Payment.PaymentStatus.COMPLETED
                )
                .exclude(student__submissions__assignment=a)
                .values_list("student__email", flat=True)
            )

            for email in students:
                if email:
                    send_mail(
                        f"⏰ {a.title} — {hours} soat qoldi",
                        f"Muddat: {a.deadline.strftime('%d.%m.%Y %H:%M')}",
                        settings.DEFAULT_FROM_EMAIL,
                        [email],
                    )


@shared_task(ignore_result=True)
def send_quiz_result_email_task(
    student_id: int, quiz_title: str, score: float, is_passed: bool
) -> None:
    """Result QUIZ ATTEMPT"""
    try:
        student = User.objects.get(id=student_id)
        status_text = "PASSED" if is_passed else "FAILED"
        send_mail(
            subject=f"Quiz Results: {quiz_title}",
            message=f"Hi {student.full_name},\n\nYou completed the quiz '{quiz_title}'.\nScore: {score}%\nStatus: {status_text}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[student.email],
            fail_silently=True,
        )
    except User.DoesNotExist:
        pass


@shared_task(ignore_result=True)
def send_certificate_ready_email_task(student_id: int, course_title: str) -> None:
    """Notification about CERTIFICATE"""
    try:
        student = User.objects.get(id=student_id)
        send_mail(
            subject=f"Your Certificate for '{course_title}' is Ready!",
            message=f"Congratulations, {student.full_name}! You have successfully completed '{course_title}'. Your certificate is now available for download in your dashboard.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[student.email],
            fail_silently=True,
        )
    except User.DoesNotExist:
        pass

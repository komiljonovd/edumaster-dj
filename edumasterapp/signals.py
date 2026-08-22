from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import (
    Course,
    Lesson,
    Question,
    Payment,
    Certificate,
    Assignment,
    AssignmentSubmission,
    Quiz,
    QuizAttempt,
)
from service.notifications.task_notifications import (
    send_new_course_email_task,
    send_certificate_ready_email_task,
    send_quiz_result_email_task,
)
from django.db import transaction


@receiver(post_delete, sender=Course)
def appointment_cache(sender, instance, **kwargs):
    cache.delete_pattern("*CourseListCreateAPI*")
    cache.delete_pattern("*CourseDetailApi*")
    print("cache deleted")


@receiver(post_save, sender=Course)
def appointment_del_cache(sender, instance, created, **kwargs):
    cache.delete_pattern("*CourseListCreateAPI*")
    cache.delete_pattern("*CourseDetailApi*")
    if created:
        transaction.on_commit(lambda: send_new_course_email_task(instance.id))
        print("cache deleted")


@receiver([post_save, post_delete], sender=Lesson)
def lesson_del_cache(sender, instance, **kwargs):
    cache.delete_pattern("*LessonDetailAPI*")


@receiver([post_save, post_delete], sender=Question)
def question_del_cache(sender, instance, **kwargs):
    cache.delete_pattern("*QuestionDetailAPI*")


@receiver([post_save, post_delete], sender=Payment)
def payment_del_cache(sender, instance, **kwargs):
    cache.delete_pattern("*PaymentListCreateAPI*")
    cache.delete_pattern("*PaymentDetailAPI*")


@receiver(post_delete, sender=Certificate)
def certificate_del_cache(sender, instance, **kwargs):
    cache.delete_pattern("*CertificateListAPI*")
    cache.delete_pattern("*CertificateDetailAPI*")
    cache.delete_pattern("*ParentChildrenReportAPIView*")


@receiver(post_save, sender=Certificate)
def certificate_del_del_cache(sender, instance, created, **kwargs):
    cache.delete_pattern("*CertificateListAPI*")
    cache.delete_pattern("*CertificateDetailAPI*")
    cache.delete_pattern("*ParentChildrenReportAPIView*")

    if created:
        transaction.on_commit(
            lambda: send_certificate_ready_email_task(
                instance.id, instance.course.title
            )
        )


@receiver([post_save, post_delete], sender=Assignment)
def assignment_del_cache(sender, instance, **kwargs):
    cache.delete_pattern("*AssignmentDetailAPI*")
    cache.delete_pattern("*AssignmentListCreateAPI*")
    cache.delete_pattern("*ParentChildrenReportAPIView*")


@receiver([post_save, post_delete], sender=AssignmentSubmission)
def assigment_sub_del_cache(sender, instance, **kwargs):
    cache.delete_pattern("*StudentCreateAssignmentAPI*")
    cache.delete_pattern("*ParentChildrenReportAPIView*")


@receiver([post_save, post_delete], sender=Quiz)
def quiz_del_cache(sender, instance, **kwargs):
    cache.delete_pattern("*QuizListCreateAPI*")
    cache.delete_pattern("*QuizDetailAPI*")
    cache.delete_pattern("*ParentChildrenReportAPIView*")


@receiver(post_save, sender=QuizAttempt)
def quiz_attempt_cache(sender, instance, created, **kwargs):
    cache.delete_pattern("*ParentChildrenReportAPIView*")
    if created:
        transaction.on_commit(
            lambda: send_quiz_result_email_task(
                instance.student.id,
                instance.quiz.title,
                instance.score,
                instance.is_passed,
            )
        )


@receiver(post_delete, sender=QuizAttempt)
def quiz_attempt_del_cache(sender, instance, **kwargs):
    cache.delete_pattern("*ParentChildrenReportAPIView*")

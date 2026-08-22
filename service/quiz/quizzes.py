

import logging
from datetime import datetime
from typing import Any, Dict, Optional
 
from django.core.cache import cache
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from edumasterapp.models import QuizAttempt,Payment,Quiz,Question
from service.tasks.certificate import generate_certificate_task
 
logger = logging.getLogger(__name__)
 
 
class QuizService:
    NETWORK_GRACE_PERIOD_SECONDS: int = 15
 
    @classmethod
    def _max_allowed_seconds(cls, quiz) -> int:
        return (quiz.time_limit_mins * 60) + cls.NETWORK_GRACE_PERIOD_SECONDS
 
    @classmethod
    def _cache_key(cls, student_id: int, quiz_id: int) -> str:
        return f"quiz_session:{student_id}:{quiz_id}"
 
    @classmethod
    def start_quiz_session(cls, student: Any, quiz_id: int) -> Dict[str, Any]:
        quiz = get_object_or_404(Quiz.objects.filter(is_deleted=False), id=quiz_id)
 
        is_paid: bool = Payment.objects.filter(
            student=student,
            course_id=quiz.course_id,
            status="completed",
        ).exists()
        if not is_paid:
            raise ValueError("Access to the QUIZ is denied.")
 
        attempts_count = QuizAttempt.objects.filter(student=student, quiz=quiz).count()
        if attempts_count >= quiz.attempts_count:
            raise ValueError("Превышен лимит попыток прохождения этого теста.")
 
        cache_key = cls._cache_key(student.id, quiz.id)
        session_data = cache.get(cache_key)
 
        # ФИКС бага: если старая сессия просрочена (студент открыл тест,
        # ушёл, вернулся позже) — не тащим протухший started_at дальше.
        # Иначе submit_and_evaluate молча обнулит честно набранные баллы.
        if session_data:
            started_at = datetime.fromisoformat(session_data["started_at"])
            elapsed = (timezone.now() - started_at).total_seconds()
            if elapsed > cls._max_allowed_seconds(quiz):
                session_data = None
                cache.delete(cache_key)
 
        if not session_data:
            session_data = {"started_at": timezone.now().isoformat()}
            ttl = cls._max_allowed_seconds(quiz) + 300
            cache.set(cache_key, session_data, timeout=ttl)
 
        return {
            "quiz_id": quiz.id,
            "title": quiz.title,
            "time_limit_mins": quiz.time_limit_mins,
            "started_at": session_data["started_at"],
        }
 
    @classmethod
    @transaction.atomic
    def submit_and_evaluate(
        cls, student: Any, quiz_id: int, submitted_answers: Optional[Dict[str, str]]
    ) -> "QuizAttempt":
        submitted_answers = submitted_answers or {}
 
        quiz = get_object_or_404(Quiz.objects.filter(is_deleted=False), id=quiz_id)
 
        cache_key = cls._cache_key(student.id, quiz.id)
        session_data: Optional[Dict[str, Any]] = cache.get(cache_key)
        if not session_data:
            raise ValueError("Сессия теста не найдена или время прохождения истекло.")
 
        started_at = datetime.fromisoformat(session_data["started_at"])
        elapsed_seconds = (timezone.now() - started_at).total_seconds()
        max_allowed_seconds = cls._max_allowed_seconds(quiz)
 
        cache.delete(cache_key)
 
        attempt = QuizAttempt(
            student=student,
            quiz=quiz,
            started_at=started_at,
            completed_at=timezone.now(),
        )
 
        if elapsed_seconds > max_allowed_seconds:
            attempt.score = 0
            attempt.is_passed = False
            attempt.save()
            return attempt
 
        # .only() — тянем из БД только то, что реально используем
        questions = Question.objects.filter(
            quiz=quiz, is_deleted=False
        ).only("id", "correct_answer", "marks")
 
        earned_marks = 0
        for question in questions:
            user_choice = submitted_answers.get(str(question.id))
            if user_choice and user_choice == question.correct_answer:
                earned_marks += question.marks
 
        attempt.score = min(earned_marks, quiz.max_score)
        attempt.is_passed = attempt.score >= quiz.min_score
        attempt.save()
 
        # ФИКС race condition: раньше .delay() вызывался ДО коммита
        # транзакции. Celery-воркер мог забрать таск и получить
        # QuizAttempt.DoesNotExist, потому что строка ещё не в БД.
        # transaction.on_commit гарантирует запуск таска только
        # после успешного коммита.
        if attempt.is_passed:
            transaction.on_commit(
                lambda: cls._enqueue_certificate(attempt.id)
            )
 
        return attempt
 
    @staticmethod
    def _enqueue_certificate(attempt_id: int) -> None:
        try:
            generate_certificate_task.delay(attempt_id)
        except Exception:
            # Брокер недоступен и т.п. — не должно ломать флоу пользователя,
            # но должно быть видно в логах/Sentry.
            logger.exception(
                "Failed to enqueue generate_certificate_task for attempt_id=%s",
                attempt_id,
            )



























# from datetime import datetime
# from typing import Dict, Any, Optional
# from django.core.cache import cache
# from django.db import transaction
# from django.shortcuts import get_object_or_404
# from django.utils import timezone

# from edumasterapp.models import Quiz, QuizAttempt, Question,Payment
# from service.tasks.certificate import generate_certificate_task

# class QuizService:
#     NETWORK_GRACE_PERIOD_SECONDS: int = 15

#     @classmethod
#     def start_quiz_session(cls, student: Any, quiz_id: int) -> Dict[str, Any]:
#         quiz = get_object_or_404(Quiz.objects.filter(is_deleted=False), id=quiz_id)

#         course_id: int = quiz.course.id
#         is_paid: bool = Payment.objects.filter(
#             student=student,
#             course_id=course_id,
#             status="completed",
#         ).exists()

#         if not is_paid:
#             raise ValueError("Access to the QUIZ is denied.")


#         # Проверка лимита (считаем попытки)
#         attempts_count = QuizAttempt.objects.filter(student=student, quiz=quiz).count()
#         if attempts_count >= quiz.attempts_count:
#             raise ValueError("Превышен лимит попыток прохождения этого теста.")

#         cache_key = f"quiz_session:{student.id}:{quiz.id}"
#         session_data = cache.get(cache_key)

#         if not session_data:
#             session_data = {"started_at": timezone.now().isoformat()}
#             ttl = (quiz.time_limit_mins * 60) + cls.NETWORK_GRACE_PERIOD_SECONDS + 300
#             cache.set(cache_key, session_data, timeout=ttl)

#         return {
#             "quiz_id": quiz.id,
#             "title": quiz.title,
#             "time_limit_mins": quiz.time_limit_mins,
#             "started_at": session_data["started_at"]
#         }

#     @classmethod
#     @transaction.atomic
#     def submit_and_evaluate(
#         cls, student: Any, quiz_id: int, submitted_answers: Dict[str, str]
#     ) -> QuizAttempt:
#         quiz = get_object_or_404(Quiz.objects.filter(is_deleted=False), id=quiz_id)

#         cache_key = f"quiz_session:{student.id}:{quiz.id}"
#         session_data: Optional[Dict[str, Any]] = cache.get(cache_key)

#         if not session_data:
#             raise ValueError("The test session was not found or the test timed out.")

#         started_at = datetime.fromisoformat(session_data["started_at"])
#         elapsed_seconds = (timezone.now() - started_at).total_seconds()
#         max_allowed_seconds = (quiz.time_limit_mins * 60) + cls.NETWORK_GRACE_PERIOD_SECONDS

#         cache.delete(cache_key)

#         # ФОРМИРУЕМ ПОПЫТКУ
#         attempt = QuizAttempt(
#             student=student,
#             quiz=quiz,
#             started_at=started_at,
#             completed_at=timezone.now()
#         )

#         # Если таймаут — провал с 0 баллов, но без 400 ошибки!
#         if elapsed_seconds > max_allowed_seconds:
#             attempt.score = 0
#             attempt.is_passed = False
#             attempt.save()
#             return attempt

#         # Считаем баллы (пустой submitted_answers просто даст 0 баллов)
#         questions = Question.objects.filter(quiz=quiz, is_deleted=False)
#         earned_marks = 0

#         for question in questions:
#             user_choice = submitted_answers.get(str(question.id))
#             if user_choice and user_choice == question.correct_answer:
#                 earned_marks += question.marks

#         attempt.score = min(earned_marks, quiz.max_score)
#         attempt.is_passed = attempt.score >= quiz.min_score
#         attempt.save()

#         # 🚀 МАГИЯ CELERY: Если тест сдан успешно, генерируем сертификат в фоне
#         if attempt.is_passed:
#             try:
#                 generate_certificate_task.delay(attempt.id)
#             except Exception as e:
#                 print(e)
#                 return attempt
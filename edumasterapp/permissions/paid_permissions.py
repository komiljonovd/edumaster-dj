from rest_framework import permissions
from ..models import Payment, Lesson, Course, Assignment, Quiz


class IsStudentPaid(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if getattr(request.user, "role", None) == "STUDENT":
            if isinstance(obj, Lesson):
                course = obj.course
                print(course)
            elif isinstance(obj, Course):
                print(course)
                course = obj

            else:
                return False

            return Payment.objects.filter(
                student=request.user, course=course, status="completed"
            ).exists()


class IsStudentAssignment(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method not in permissions.SAFE_METHODS:
            return False
        if getattr(request.user, "role", None) != "STUDENT":
            return False

        course = obj.lesson.course
        return Payment.objects.filter(
            student=request.user,
            course=course,
            status=Payment.PaymentStatus.COMPLETED,
        ).exists()


class IsStudentHasQuiz(permissions.BasePermission):

    message: str = "Доступ запрещен."

    def has_permission(self, request, view) -> bool:
        user = request.user

        # 1. Проверка авторизации и роли
        if not (
            user and user.is_authenticated and getattr(user, "role", None) == "STUDENT"
        ):
            self.message = "Только авторизованные студенты могут проходить тесты."
            return False

        # 2. Получение ID квиза из URL
        quiz_id = view.kwargs.get("quiz_id") or view.kwargs.get("pk")
        if not quiz_id:
            self.message = "ID теста не передан."
            return False

        # 3. Поиск квиза и определение ID курса
        try:
            quiz = Quiz.objects.select_related("lesson__course").get(
                id=quiz_id, is_deleted=False
            )
        except Quiz.DoesNotExist:
            self.message = "Тест не найден или удален."
            return False

        request.quiz = quiz
        course_id: int = (
            quiz.lesson.course_id
            if hasattr(quiz, "lesson")
            else getattr(quiz, "course_id", None)
        )

        # 4. Проверка успешной оплаты курса
        is_paid = Payment.objects.filter(
            student=user, course_id=course_id, status="completed"
        ).exists()

        if not is_paid:
            self.message = "Курс не оплачен. Доступ к тестированию закрыт."
            return False

        return True

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse_lazy
from edumasterapp.models import (
    Course,
    Category,
    Quiz,
)

from django.contrib.auth import get_user_model

User = get_user_model()


class TestQuizTestCase(APITestCase):
    def setUp(self) -> None:
        super().setUp()
        self.teacher = User.objects.create_user(
            email="teacher@test.com", password="123", role="TEACHER"
        )
        self.student = User.objects.create_user(
            email="student@test.com", password="123", role="STUDENT"
        )

        self.category = Category.objects.create(name="Biology")

        self.course = Course.objects.create(
            title="Biology",
            price=1500000,
            duration=12,
            author=self.teacher,
            category=self.category,
        )

        self.quiz_list_url = reverse_lazy("quiz-list-create")

        self.quiz = Quiz.objects.create(
            course=self.course,
            title="Initial Quiz",
            time_limit_mins=20,
            attempts_count=3,
            min_score=60,
            max_score=100,
        )

    def test_teacher_can_create_quiz(self) -> None:
        self.client.force_authenticate(user=self.teacher)

        data = {
            "course": self.course.pk,
            "title": "Midterm Exam",
            "description": "Important test",
            "time_limit_mins": 30,
            "attempts_count": 2,
            "min_score": 50,
            "max_score": 100,
        }

        response = self.client.post(self.quiz_list_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Midterm Exam")

    def test_teacher_can_update_quiz(self) -> None:
        self.client.force_authenticate(user=self.teacher)

        quiz_detail_url = reverse_lazy("quiz-detail", kwargs={"pk": self.quiz.pk})

        data = {"title": "Updated Quiz Title", "time_limit_mins": 45}

        response = self.client.patch(quiz_detail_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.quiz.refresh_from_db()
        self.assertEqual(self.quiz.title, "Updated Quiz Title")

    def test_teacher_can_soft_delete_quiz(self) -> None:
        self.client.force_authenticate(user=self.teacher)

        quiz_detail_url = reverse_lazy("quiz-detail", kwargs={"pk": self.quiz.pk})
        response = self.client.delete(quiz_detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.quiz.refresh_from_db()
        self.assertTrue(self.quiz.is_deleted)

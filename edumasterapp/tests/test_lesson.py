from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse_lazy
from django.utils import timezone

from edumasterapp.models import (
    Course,
    Lesson,
    Category,
)
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model

User = get_user_model()

dummy_pdf = SimpleUploadedFile(
    name="test_lesson.pdf",
    content=b"dummy pdf content",
    content_type="application/pdf",
)

dummy_video = SimpleUploadedFile(
    name="test_video.mp4",
    content=b"dummy video content",
    content_type="video/mp4",
)


class TestLessonAPI(APITestCase):
    def setUp(self) -> None:
        super().setUp()
        self.teacher = User.objects.create_user(
            email="teacher@test.com", password="123", role="TEACHER"
        )
        self.admin = User.objects.create_user(
            email="admin123@test.com", password="123", role="ADMIN"
        )

        self.category = Category.objects.create(name="Mathematics")

        self.course = Course.objects.create(
            title="Math",
            price=1500000,
            duration=6,
            author=self.teacher,
            category=self.category,
        )
        self.lesson_list_url = reverse_lazy("lesson-create")
        self.lesson_detail = reverse_lazy("lesson-detail")

    def test__teacher_can_create_lesson(self) -> None:
        self.client.force_authenticate(user=self.teacher)
        data = {
            "course": self.course.pk,
            "title": "Node.js",
            "description": "Backend",
            "order": 2,
            "pdf": dummy_pdf,
            "video": dummy_video,
            "duration": 45,
        }
        response = self.client.post(self.lesson_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test__duplicate_order_number_validation(self) -> None:
        Lesson.objects.create(course=self.course, title="Intro", order=1, duration=10)

        self.client.force_authenticate(user=self.teacher)
        data = {
            "course": self.course.pk,
            "title": "Conflict",
            "order": 1,
            "duration": 30,
        }
        response = self.client.post(self.lesson_list_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test__get_lesson_detail(
        self,
    ) -> None:
        lesson = Lesson.objects.create(
            course=self.course,
            title="Intro",
            order=1,
            duration=10,
        )

        lesson_detail_url = reverse_lazy("lesson-detail", kwargs={"pk": lesson.pk})
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(lesson_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse_lazy
from django.utils import timezone

from edumasterapp.models import (
    Payment,
    Payment,
    Course,
    Lesson,
    Assignment,
    AssignmentSubmission,
    Quiz,
    QuizAttempt,
    Category,
)
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model

User = get_user_model()


class TestCourseAPI(APITestCase):
    def setUp(self) -> None:
        super().setUp()
        self.super_admin = User.objects.create_user(
            email="admin@test.com", password="123", role="SUPER_ADMIN"
        )
        self.student = User.objects.create_user(
            email="student@test.com", password="123", role="STUDENT"
        )
        self.course_list_url = reverse_lazy("course-list-create")

        self.category = Category.objects.create(name="Programming")

        self.course = Course.objects.create(
            title="Python Foundation",
            price=1000,
            duration=6,
            author=self.super_admin,
            category=self.category,
        )
        self.course_detail_url = reverse_lazy(
            "course-detail", kwargs={"pk": self.course.pk}
        )

    def test__admin_can_create_course(self) -> None:
        self.client.force_authenticate(user=self.super_admin)

        image_data = b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b"
        test_image = SimpleUploadedFile(
            name="cover.png", content=image_data, content_type="image/png"
        )

        data = {
            "title": "Django REST",
            "description": "Backend API",
            "price": 1500,
            "duration": 6,
            "category": self.category.pk,
            "image": test_image,
        }

        response = self.client.post(self.course_list_url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test__student_cannot_create_course(self) -> None:
        self.client.force_authenticate(user=self.student)
        response = self.client.post(
            self.course_list_url,
            {
                "title": "Django REST",
                "description": "Backend API",
                "price": 1500,
                "duration": 6,
                "author_id": self.student,
                "category": "Backend",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test__admin_can_soft_delete_course(self) -> None:
        self.client.force_authenticate(user=self.super_admin)
        response = self.client.delete(self.course_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.course.refresh_from_db()
        self.assertTrue(self.course.is_deleted)

    def test_student_list_course(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.course_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

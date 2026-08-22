from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse_lazy
from edumasterapp.models import (
    Course,
    Lesson,
    Assignment,
    AssignmentSubmission,
    Category,
    Payment,
)
import uuid
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class TestStudentSubmitAssignmentAPI(APITestCase):
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

        self.lesson = Lesson.objects.create(
            course=self.course, title="Cells", order=1, duration=45
        )

        self.assignment = Assignment.objects.create(
            lesson=self.lesson,
            title="HW",
            deadline=timezone.now() + timezone.timedelta(days=2),
        )

        Payment.objects.create(
            student=self.student,
            course=self.course,
            amount=1500000,
            status="completed",
            method="payme",
            transaction_id=uuid.uuid4(),
        )

        self.student_submit_url = reverse_lazy("student-assignment-create")

    def test_1_student_can_submit_assignment_successfully(self) -> None:
        self.client.force_authenticate(user=self.student)

        test_file = SimpleUploadedFile(
            name="homework.txt",
            content=b"Here are my answers",
            content_type="text/plain",
        )

        data = {
            "student": self.student.pk,
            "assignment": self.assignment.pk,
            "file": test_file,
            "student_comment": "Done!",
        }

        response = self.client.post(self.student_submit_url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_2_teacher_cannot_submit_as_student(self) -> None:
        self.client.force_authenticate(user=self.teacher)

        test_file = SimpleUploadedFile("hw.txt", b"data", content_type="text/plain")
        data = {"assignment": self.assignment.pk, "file": test_file}

        response = self.client.post(self.student_submit_url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_3_submission_after_deadline_fails(self) -> None:
        past_assignment = Assignment.objects.create(
            lesson=self.lesson,
            title="Late",
            deadline=timezone.now() - timezone.timedelta(days=1),  # Дедлайн в прошлом
        )

        self.client.force_authenticate(user=self.student)
        test_file = SimpleUploadedFile("late.txt", b"late", content_type="text/plain")

        response = self.client.post(
            self.student_submit_url,
            {"assignment": past_assignment.pk, "file": test_file},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_4_duplicate_submission_fails(self) -> None:
        AssignmentSubmission.objects.create(
            student=self.student,
            assignment=self.assignment,
            student_comment="First try",
        )

        self.client.force_authenticate(user=self.student)
        test_file = SimpleUploadedFile(
            "second.txt", b"second", content_type="text/plain"
        )

        response = self.client.post(
            self.student_submit_url,
            {"assignment": self.assignment.pk, "file": test_file},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

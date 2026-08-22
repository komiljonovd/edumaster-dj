from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse_lazy
from edumasterapp.models import (
    Course,
    Category,
    Quiz,
    Payment,
)
from userapp.models import ParentChild
from django.contrib.auth import get_user_model

User = get_user_model()


class TestPaymentAPI(APITestCase):
    def setUp(self) -> None:
        super().setUp()

        self.teacher = User.objects.create_user(
            email="teacher@test.com", password="123", role="TEACHER"
        )
        self.student = User.objects.create_user(
            email="student@test.com", password="123", role="STUDENT"
        )
        self.parent = User.objects.create_user(
            email="parent@test.com", password="123", role="PARENT"
        )
        self.admin = User.objects.create_superuser(
            email="admin@test.com", password="123"
        )

        ParentChild.objects.create(
            parent=self.parent, student=self.student, is_confirmed=True
        )

        self.category = Category.objects.create(name="IT")
        self.course = Course.objects.create(
            title="Pro",
            price=1000,
            duration=6,
            author=self.teacher,
            category=self.category,
        )

        self.payment_url = reverse_lazy("payment-create")

    def test_21_teacher_cannot_create_payment(self) -> None:
        """Teacher не входит в IsSuperAdmin | IsStudent -> 403."""
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(
            self.payment_url,
            {"course": self.course.pk, "amount": 1000, "method": "CLICK"},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_22_parent_cannot_access_payment_list(self) -> None:

        Payment.objects.create(
            student=self.student,
            course=self.course,
            amount=1000,
            method="Click",
            status="completed",
        )

        self.client.force_authenticate(user=self.parent)
        response = self.client.get(f"{self.payment_url}?student_id={self.student.pk}")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_23_student_sees_only_own_payments(self) -> None:
        other_student = User.objects.create_user(
            email="student2@test.com", password="123", role="STUDENT"
        )
        Payment.objects.create(
            student=self.student,
            course=self.course,
            amount=1000,
            method="click",
            status="completed",
        )
        Payment.objects.create(
            student=other_student,
            course=self.course,
            amount=1000,
            method="click",
            status="completed",
        )

        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.payment_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get("results", response.data)
        self.assertEqual(len(results), 1)

    def test_24_superadmin_sees_all_payments(self) -> None:
        Payment.objects.create(
            student=self.student,
            course=self.course,
            amount=1000,
            method="click",
            status="completed",
        )

        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.payment_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get("results", response.data)
        self.assertEqual(len(results), 1)

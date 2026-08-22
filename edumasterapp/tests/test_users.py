from rest_framework.test import APITestCase
from rest_framework import status
from django.utils import timezone
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model

User = get_user_model()


class TestAuthenticationAPI(APITestCase):
    def setUp(self) -> None:
        self.register_url = reverse_lazy("register")
        self.login_url = reverse_lazy("token_obtain_pair")
        self.profile = reverse_lazy("profile")

        self.user = User.objects.create_user(
            email="dilshod@test.com", password="strongpassword123", role="STUDENT"
        )

    def test_user_registration_success(self):
        data = {
            "email": "new@test.com",
            "password": "newpassword123",
            "password_confirm": "newpassword123",
            "first_name": "Alex",
            "last_name": "Volkov",
            "role": "STUDENT",
            "gender": "MALE",
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_login_success(self):
        data = {"email": "dilshod@test.com", "password": "strongpassword123"}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_invalid_credentials_fails(self) -> None:
        data = {"email": "student@test.com", "password": "wrong"}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

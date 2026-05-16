from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()


class UsersAuthTests(APITestCase):
    def test_register_returns_tokens_and_user(self):
        response = self.client.post(
            reverse("register"),
            {
                "email": "student@example.com",
                "password": "StrongPass123!",
                "role": "jobseeker",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["email"], "student@example.com")

    def test_login_with_email_returns_tokens(self):
        User.objects.create_user(
            username="student@example.com",
            email="student@example.com",
            password="StrongPass123!",
            role="jobseeker",
        )

        response = self.client.post(
            reverse("login"),
            {
                "email": "student@example.com",
                "password": "StrongPass123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["email"], "student@example.com")

    def test_login_with_wrong_password_fails(self):
        User.objects.create_user(
            username="student@example.com",
            email="student@example.com",
            password="StrongPass123!",
            role="jobseeker",
        )

        response = self.client.post(
            reverse("login"),
            {
                "email": "student@example.com",
                "password": "WrongPassword",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

#e
    def test_profile_requires_authentication(self):
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
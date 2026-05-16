from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()


class ChatTests(APITestCase):

    def setUp(self):
        self.sender = User.objects.create_user(
            username="sender",
            email="sender@test.com",
            password="12345678",
            role="jobseeker"
        )

        self.recipient = User.objects.create_user(
            username="recipient",
            email="recipient@test.com",
            password="12345678",
            role="recruiter"
        )

    def test_send_encrypted_message(self):
        self.client.force_authenticate(user=self.sender)

        response = self.client.post(
            f"/api/chat/{self.recipient.id}/",
            {"encrypted_text": "Hello!"},
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data
        )

    def test_retrieve_conversation(self):
        self.client.force_authenticate(user=self.sender)

        self.client.post(
            f"/api/chat/{self.recipient.id}/",
            {"encrypted_text": "Hello!"},
            format="json"
        )

        response = self.client.get(
            f"/api/chat/{self.recipient.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data
        )

    def test_message_to_non_existent_user(self):
        self.client.force_authenticate(user=self.sender)

        response = self.client.post(
        "/api/chat/99999/",
        {"encrypted_text": "Hello!"},
        format="json"
        )

        self.assertEqual(
        response.status_code,
        status.HTTP_404_NOT_FOUND
        )

    def test_unauthenticated_message_attempt(self):
        response = self.client.post(
            f"/api/chat/{self.recipient.id}/",
            {"encrypted_text": "Hello!"},
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )
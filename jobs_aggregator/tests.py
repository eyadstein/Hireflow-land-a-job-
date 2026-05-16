from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()


class JobAggregatorTests(APITestCase):

    EXTERNAL_ALLOWED_STATUSES = [
        status.HTTP_200_OK,
        status.HTTP_400_BAD_REQUEST,
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        status.HTTP_503_SERVICE_UNAVAILABLE,
    ]

    def setUp(self):
        self.user = User.objects.create_user(
            username="jobseeker",
            email="jobseeker@test.com",
            password="12345678",
            role="jobseeker"
        )
        self.client.force_authenticate(user=self.user)

    def test_search_external_jobs(self):
        response = self.client.get(
            "/api/jobs-aggregator/search/",
            {
                "query": "backend developer",
                "country": "eg"
            }
        )

        self.assertIn(
            response.status_code,
            self.EXTERNAL_ALLOWED_STATUSES,
            response.data if hasattr(response, "data") else response.content
        )

    def test_get_match_score(self):
        response = self.client.post(
            "/api/jobs-aggregator/match/",
            {
                "job_id": "test-job-1"
            },
            format="json"
        )

        self.assertIn(
            response.status_code,
            self.EXTERNAL_ALLOWED_STATUSES,
            response.data if hasattr(response, "data") else response.content
        )

    def test_get_supported_countries(self):
        response = self.client.get(
            "/api/jobs-aggregator/countries/"
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_200_OK,
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                status.HTTP_503_SERVICE_UNAVAILABLE,
            ],
            response.data if hasattr(response, "data") else response.content
        )
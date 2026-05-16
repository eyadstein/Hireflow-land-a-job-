from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

from jobs.models import Job

User = get_user_model()


class ApplicationTests(APITestCase):

    def setUp(self):
        self.recruiter = User.objects.create_user(
            username="recruiter",
            email="recruiter@test.com",
            password="12345678",
            role="recruiter"
        )

        self.jobseeker = User.objects.create_user(
            username="jobseeker",
            email="jobseeker@test.com",
            password="12345678",
            role="jobseeker"
        )

        self.job = Job.objects.create(
            title="Backend Developer",
            company="HireFlow",
            description="Django Developer",
            location="Cairo",
            posted_by=self.recruiter
        )

    def test_submit_valid_application(self):
        self.client.force_authenticate(user=self.jobseeker)

        response = self.client.post(
            "/api/applications/apply/",
            {"job_id": self.job.id},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
def test_duplicate_application(self):
    self.client.force_authenticate(user=self.jobseeker)

    self.client.post(
        "/api/applications/apply/",
        {"job_id": self.job.id},
        format="json"
    )

    response = self.client.post(
        "/api/applications/apply/",
        {"job_id": self.job.id},
        format="json"
    )

    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
def test_view_own_applications(self):
    self.client.force_authenticate(user=self.jobseeker)

    self.client.post(
        "/api/applications/apply/",
        {"job_id": self.job.id},
        format="json"
    )

    response = self.client.get("/api/applications/mine/")

    self.assertEqual(response.status_code, status.HTTP_200_OK)

    data = response.data.get("results", response.data) if isinstance(response.data, dict) else response.data
    self.assertGreaterEqual(len(data), 1)
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from applications.models import Application

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
def test_recruiter_views_job_applications(self):
    self.client.force_authenticate(user=self.jobseeker)
    self.client.post(
        "/api/applications/apply/",
        {"job_id": self.job.id},
        format="json"
    )
    self.client.force_authenticate(user=self.recruiter)
    response = self.client.get(f"/api/applications/job/{self.job.id}/")
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    
def test_update_application_status(self):
    application = Application.objects.create(
        job=self.job,
        applicant=self.jobseeker,
        status="pending"
    )
    self.client.force_authenticate(user=self.recruiter)
    response = self.client.patch(
        f"/api/applications/{application.id}/status/",
        {"status": "interview"},
        format="json"
    )
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    
def test_invalid_status_value(self):
    application = Application.objects.create(
        job=self.job,
        applicant=self.jobseeker,
        status="pending"
    )
    self.client.force_authenticate(user=self.recruiter)
    response = self.client.patch(
        f"/api/applications/{application.id}/status/",
        {"status": "hired"},
        format="json"
    )
    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
def test_non_owner_cannot_update_status(self):
    other_recruiter = User.objects.create_user(
        username="otherrecruiter",
        email="other@test.com",
        password="12345678",
        role="recruiter"
    )
    application = Application.objects.create(
        job=self.job,
        applicant=self.jobseeker,
        status="pending"
    )
    self.client.force_authenticate(user=other_recruiter)
    response = self.client.patch(
        f"/api/applications/{application.id}/status/",
        {"status": "interview"},
        format="json"
    )
    self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
def test_reject_all_pending(self):
    Application.objects.create(
        job=self.job,
        applicant=self.jobseeker,
        status="pending"
    )
    self.client.force_authenticate(user=self.recruiter)
    response = self.client.post(
        "/api/applications/reject-all-pending/",
        {"job_id": self.job.id},
        format="json"
    )
    self.assertEqual(response.status_code, status.HTTP_200_OK)
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


class JobTests(APITestCase):

    def setUp(self):
        self.recruiter = User.objects.create_user(
            username="recruiter",
            email="recruiter@test.com",
            password="12345678",
            role="recruiter"
        )

    def test_recruiter_can_create_job(self):
        self.client.force_authenticate(user=self.recruiter)

        data = {
            "title": "Backend Developer",
            "company": "HireFlow",
            "description": "Django Developer",
            "location": "Cairo"
        }

        response = self.client.post("/api/jobs/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_job_missing_title(self):
        self.client.force_authenticate(user=self.recruiter)

        data = {
            "company": "HireFlow",
            "description": "Django Developer",
            "location": "Cairo"
        }

        response = self.client.post("/api/jobs/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    def test_list_jobs(self):
        self.client.force_authenticate(user=self.recruiter)

        response = self.client.get("/api/jobs/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
    def test_jobseeker_cannot_create_job(self):

        jobseeker = User.objects.create_user(
            username="jobseeker",
            email="job@test.com",
            password="12345678",
            role="jobseeker"
        )

        self.client.force_authenticate(user=jobseeker)

        data = {
            "title": "Frontend Developer",
            "company": "HireFlow",
            "description": "React Job",
            "location": "Cairo"
        }

        response = self.client.post("/api/jobs/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

def test_unauthenticated_user_cannot_create_job(self):

    data = {
        "title": "Backend Developer",
        "company": "HireFlow",
        "description": "Django Developer",
        "location": "Cairo"
    }

    response = self.client.post("/api/jobs/", data, format="json")

    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
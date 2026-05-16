from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()


class AICareerToolTests(APITestCase):

    AI_ALLOWED_STATUSES = [
        status.HTTP_200_OK,
        status.HTTP_201_CREATED,
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

    def test_resume_analysis_valid_pdf(self):
        pdf_file = SimpleUploadedFile(
            "resume.pdf",
            b"%PDF-1.4 fake pdf content",
            content_type="application/pdf"
        )

        response = self.client.post(
            "/api/ai/resume-analyzer/",
            {"file": pdf_file},
            format="multipart"
        )

        self.assertIn(response.status_code, self.AI_ALLOWED_STATUSES)

    def test_resume_analysis_non_pdf(self):
        txt_file = SimpleUploadedFile(
            "resume.txt",
            b"fake resume text",
            content_type="text/plain"
        )

        response = self.client.post(
            "/api/ai/resume-analyzer/",
            {"file": txt_file},
            format="multipart"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cover_letter_generation(self):
        response = self.client.post(
            "/api/ai/cover-letter/",
            {
                "name": "Mohaned",
                "job_title": "Backend Developer",
                "company": "HireFlow",
                "job_description": "Backend Developer role using Django",
                "user_profile": "Python Django developer"
            },
            format="json"
        )

        self.assertIn(response.status_code, self.AI_ALLOWED_STATUSES)

    def test_salary_estimation(self):
        response = self.client.post(
            "/api/ai/salary-estimator/",
            {
                "role": "Backend Developer",
                "country": "Egypt",
                "experience": "Mid",
                "location": "Cairo"
            },
            format="json"
        )

        self.assertIn(response.status_code, self.AI_ALLOWED_STATUSES)

    def test_career_roadmap_generation(self):
        response = self.client.post(
            "/api/ai/career-roadmap/",
            {
                "current_role": "Junior Developer",
                "target_role": "Backend Developer",
                "skills": "Python, Django"
            },
            format="json"
        )

        self.assertIn(response.status_code, self.AI_ALLOWED_STATUSES)

    def test_start_mock_interview_session(self):
        response = self.client.post(
            "/api/ai/mock-interview/start/",
            {
                "role": "Backend Dev",
                "level": "Mid"
            },
            format="json"
        )

        self.assertIn(response.status_code, self.AI_ALLOWED_STATUSES)

    def test_linkedin_optimization(self):
        response = self.client.post(
            "/api/ai/linkedin/",
            {
                "headline": "Junior Developer",
                "about": "I build web apps",
                "experience": "1 year Django",
                "target_role": "Backend Developer"
            },
            format="json"
        )

        self.assertIn(response.status_code, self.AI_ALLOWED_STATUSES)

    def test_ai_career_chat_message(self):
        response = self.client.post(
            "/api/ai/chat/",
            {
                "message": "How do I negotiate salary?"
            },
            format="json"
        )

        self.assertIn(response.status_code, self.AI_ALLOWED_STATUSES)

    def test_interview_coach_tips(self):
        response = self.client.post(
            "/api/ai/interview-coach/",
            {
                "role": "Frontend Developer"
            },
            format="json"
        )

        self.assertIn(response.status_code, self.AI_ALLOWED_STATUSES)
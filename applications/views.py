import os
import json
from google import genai
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Application
from .serializers import ApplicationSerializer, MoveCardSerializer
from jobs.models import Job

GEMINI_KEY = os.environ.get('GEMINI_KEY', 'YOUR_GEMINI_KEY_HERE')
client     = genai.Client(api_key=GEMINI_KEY)


def ask_gemini(prompt):
    return client.models.generate_content(
        model='gemini-2.0-flash',
        contents=prompt,
    ).text


def user_applications(request):
    return Application.objects.filter(user=request.user)


# ─────────────────────────────────────────────
#  Kanban CRUD (Step 5)
# ─────────────────────────────────────────────
class ApplicationListCreateView(generics.ListCreateAPIView):
    serializer_class   = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return user_applications(self.request)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ApplicationDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return user_applications(self.request)


class KanbanBoardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        all_apps = user_applications(request).select_related('job')

        board = []
        for col_status, col_label in Application.KANBAN_STATUS_CHOICES:
            cards = all_apps.filter(status=col_status)
            board.append({
                'status': col_status,
                'label':  col_label,
                'cards':  ApplicationSerializer(cards, many=True).data,
            })

        return Response({
            'board': board,
            'total': all_apps.count(),
        })


class MoveCardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        application = get_object_or_404(
            Application, pk=pk, user=request.user
        )
        serializer = MoveCardSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        application.status = serializer.validated_data['status']
        if 'order' in serializer.validated_data:
            application.order = serializer.validated_data['order']
        application.save(update_fields=['status', 'order', 'updated_at'])

        return Response(ApplicationSerializer(application).data)


# ─────────────────────────────────────────────
#  Quick Apply with AI (Step 18)
# ─────────────────────────────────────────────
class QuickApplyView(APIView):
    """
    POST /api/applications/quick-apply/
    Body: { "job_id": 1 }
    AI reads user profile, writes cover letter, matches skills, applies.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        job_id = request.data.get('job_id')

        if not job_id:
            return Response({'error': 'job_id is required'}, status=400)

        try:
            job = Job.objects.get(pk=job_id)
        except Job.DoesNotExist:
            return Response({'error': 'Job not found'}, status=404)

        if Application.objects.filter(user=request.user, job=job).exists():
            return Response(
                {'error': 'You have already applied to this job'},
                status=400
            )

        user = request.user

        # Try to get CV profile for richer context
        try:
            from ai_features.models import CVProfile
            cv = CVProfile.objects.filter(user=user).order_by('-created_at').first()
            user_profile = f"""
Name: {cv.full_name}
Title: {cv.title}
Summary: {cv.enhanced_summary or cv.summary}
Skills: {', '.join(cv.skills)}
Experience: {json.dumps(cv.enhanced_experience or cv.experience)}
Education: {json.dumps(cv.education)}
Languages: {', '.join(cv.languages)}
""" if cv else f"Name: {user.get_full_name() or user.username}\nRole: Job Seeker"
        except Exception:
            user_profile = f"Name: {user.get_full_name() or user.username}\nRole: Job Seeker"

        job_info = f"""
Job Title: {job.title}
Company: {job.company}
Location: {job.location}
Salary: {job.salary}
Description: {job.description}
"""

        # AI — cover letter + skill matching in one call
        prompt = f"""
You are an expert career coach and application specialist.
A job seeker wants to quick-apply to a job. Do two things:

1. Write a personalized, professional cover letter (3 paragraphs max)
2. Analyze skill match between the candidate and job

Candidate Profile:
{user_profile}

Job Details:
{job_info}

Return ONLY a JSON object:
{{
  "cover_letter": "<professional cover letter text>",
  "match_score": <0-100>,
  "matched_skills": ["<skill1>", "<skill2>", "<skill3>"],
  "missing_skills": ["<skill1>", "<skill2>"],
  "match_summary": "<1 sentence summary of fit>"
}}
Return ONLY the JSON, no markdown.
"""
        try:
            result = ask_gemini(prompt)
            clean  = result.replace('```json', '').replace('```', '').strip()
            ai_data = json.loads(clean)
        except Exception:
            ai_data = {
                'cover_letter':   f"Dear Hiring Manager,\n\nI am excited to apply for the {job.title} position at {job.company}.\n\nBest regards,\n{user.get_full_name() or user.username}",
                'match_score':    50,
                'matched_skills': [],
                'missing_skills': [],
                'match_summary':  'AI analysis unavailable',
            }

        application = Application.objects.create(
            user              = user,
            job               = job,
            job_title         = job.title,
            company_name      = job.company,
            status            = 'applied',
            applied_date      = timezone.now().date(),
            quick_apply       = True,
            ai_cover_letter   = ai_data.get('cover_letter', ''),
            ai_match_score    = ai_data.get('match_score'),
            ai_matched_skills = ai_data.get('matched_skills', []),
            ai_missing_skills = ai_data.get('missing_skills', []),
            notes             = ai_data.get('match_summary', ''),
        )

        return Response({
            'id':               application.id,
            'job_title':        job.title,
            'company':          job.company,
            'status':           application.status,
            'quick_apply':      True,
            'ai_cover_letter':  application.ai_cover_letter,
            'ai_match_score':   application.ai_match_score,
            'ai_matched_skills': application.ai_matched_skills,
            'ai_missing_skills': application.ai_missing_skills,
            'match_summary':    ai_data.get('match_summary', ''),
            'applied_at':       application.created_at.strftime('%Y-%m-%d'),
        }, status=201)


class QuickApplyDashboardView(APIView):
    """
    GET /api/applications/quick-apply/history/
    Returns all quick applies with AI data.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        apps = Application.objects.filter(
            user=request.user,
            quick_apply=True
        ).select_related('job').order_by('-created_at')

        return Response([
            {
                'id':                application.id,
                'job_title':         application.get_display_title(),
                'company':           application.get_display_company(),
                'status':            application.status,
                'ai_match_score':    application.ai_match_score,
                'ai_matched_skills': application.ai_matched_skills,
                'ai_missing_skills': application.ai_missing_skills,
                'ai_cover_letter':   application.ai_cover_letter,
                'applied_at':        application.created_at.strftime('%Y-%m-%d'),
            }
            for application in apps
        ])
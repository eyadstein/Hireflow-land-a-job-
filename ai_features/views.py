import os
import json
import google.generativeai as genai
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from .agent import HireBotAgent
from .models import CareerRoadmap

GEMINI_KEY = os.environ.get('GEMINI_KEY', 'YOUR_GEMINI_KEY_HERE')
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')


def ask_gemini(prompt):
    response = model.generate_content(prompt)
    return response.text


# ─────────────────────────────────────────────
#  Existing Views (unchanged)
# ─────────────────────────────────────────────
class ResumeAnalyzerView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        resume_text = request.data.get('resume_text', '')
        job_description = request.data.get('job_description', '')

        if not resume_text:
            return Response({'error': 'resume_text is required'}, status=400)

        prompt = f"""
You are an expert ATS system and career coach.
Analyze this resume and return ONLY a JSON object with this structure:
{{
  "atsScore": <0-100>,
  "overallRating": "<Excellent|Good|Average|Poor>",
  "summary": "<2-3 sentence assessment>",
  "strengths": ["<s1>", "<s2>", "<s3>"],
  "weaknesses": ["<w1>", "<w2>", "<w3>"],
  "missingKeywords": ["<k1>", "<k2>", "<k3>", "<k4>", "<k5>"],
  "suggestions": [
    {{"priority": "High", "tip": "<tip>"}},
    {{"priority": "Medium", "tip": "<tip>"}},
    {{"priority": "Low", "tip": "<tip>"}}
  ],
  "estimatedRole": "<job title>",
  "experienceLevel": "<Junior|Mid|Senior|Executive>"
}}
{f'Job Description: {job_description}' if job_description else ''}
Resume: {resume_text}
Return ONLY the JSON, no markdown.
"""
        try:
            result = ask_gemini(prompt)
            clean = result.replace('```json', '').replace('```', '').strip()
            return Response(json.loads(clean))
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class CoverLetterView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        name = request.data.get('name', '')
        job_title = request.data.get('job_title', '')
        company = request.data.get('company', '')
        skills = request.data.get('skills', '')
        job_description = request.data.get('job_description', '')

        if not all([name, job_title, company]):
            return Response({'error': 'name, job_title, company are required'}, status=400)

        prompt = f"""
Write a professional cover letter for:
- Applicant: {name}
- Applying for: {job_title} at {company}
- Skills: {skills}
- Job Description: {job_description}

Write a compelling, personalized cover letter. 3-4 paragraphs. Professional tone.
Return ONLY the cover letter text, no extra explanation.
"""
        try:
            result = ask_gemini(prompt)
            return Response({'cover_letter': result})
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class SalaryEstimatorView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        role = request.data.get('role', '')
        country = request.data.get('country', '')
        experience_years = request.data.get('experience_years', 0)
        skills = request.data.get('skills', '')

        if not all([role, country]):
            return Response({'error': 'role and country are required'}, status=400)

        prompt = f"""
You are a salary expert for the Arab world job market.
Estimate the salary for:
- Role: {role}
- Country: {country}
- Experience: {experience_years} years
- Skills: {skills}

Return ONLY a JSON object:
{{
  "minSalary": <number in USD/month>,
  "maxSalary": <number in USD/month>,
  "avgSalary": <number in USD/month>,
  "currency": "<local currency>",
  "minLocal": <number in local currency/month>,
  "maxLocal": <number in local currency/month>,
  "avgLocal": <number in local currency/month>,
  "marketDemand": "<High|Medium|Low>",
  "topSkills": ["<skill1>", "<skill2>", "<skill3>"],
  "insight": "<2 sentence market insight>"
}}
Return ONLY the JSON, no markdown.
"""
        try:
            result = ask_gemini(prompt)
            clean = result.replace('```json', '').replace('```', '').strip()
            return Response(json.loads(clean))
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class InterviewCoachView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        role = request.data.get('role', '')
        level = request.data.get('level', 'Mid')
        job_description = request.data.get('job_description', '')

        if not role:
            return Response({'error': 'role is required'}, status=400)

        prompt = f"""
Generate interview questions and answers for:
- Role: {role}
- Level: {level}
- Job Description: {job_description}

Return ONLY a JSON object:
{{
  "technical": [
    {{"question": "<q>", "answer": "<a>", "difficulty": "<Easy|Medium|Hard>"}},
    {{"question": "<q>", "answer": "<a>", "difficulty": "<Easy|Medium|Hard>"}},
    {{"question": "<q>", "answer": "<a>", "difficulty": "<Easy|Medium|Hard>"}}
  ],
  "behavioral": [
    {{"question": "<q>", "answer": "<a>"}},
    {{"question": "<q>", "answer": "<a>"}},
    {{"question": "<q>", "answer": "<a>"}}
  ],
  "tips": ["<tip1>", "<tip2>", "<tip3>"]
}}
Return ONLY the JSON, no markdown.
"""
        try:
            result = ask_gemini(prompt)
            clean = result.replace('```json', '').replace('```', '').strip()
            return Response(json.loads(clean))
        except Exception as e:
            return Response({'error': str(e)}, status=500)


agent_sessions = {}


class AgentChatView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user_id = request.user.id
        message = request.data.get('message', '')
        user_context = request.data.get('context', '')
        reset = request.data.get('reset', False)

        if not message:
            return Response({'error': 'message is required'}, status=400)

        if reset or user_id not in agent_sessions:
            agent_sessions[user_id] = HireBotAgent()

        agent = agent_sessions[user_id]

        try:
            result = agent.run(message, user_context)
            return Response(result)
        except Exception as e:
            return Response({'error': str(e)}, status=500)


# ─────────────────────────────────────────────
#  NEW — Career Roadmap Generation
# ─────────────────────────────────────────────
class CareerRoadmapView(APIView):
    """
    POST /api/ai/career-roadmap/   → generate + save a new roadmap
    GET  /api/ai/career-roadmap/   → list user's saved roadmaps
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        roadmaps = CareerRoadmap.objects.filter(user=request.user)
        data = [
            {
                'id':           r.id,
                'current_role': r.current_role,
                'target_role':  r.target_role,
                'experience':   r.experience,
                'skills':       r.skills,
                'roadmap':      r.roadmap,
                'created_at':   r.created_at.strftime('%Y-%m-%d'),
            }
            for r in roadmaps
        ]
        return Response(data)

    def post(self, request):
        current_role = request.data.get('current_role', '')
        target_role  = request.data.get('target_role', '')
        experience   = request.data.get('experience', '')
        skills       = request.data.get('skills', '')

        if not all([current_role, target_role]):
            return Response(
                {'error': 'current_role and target_role are required'},
                status=400
            )

        prompt = f"""
You are an expert career coach specializing in the Arab world tech job market.
Create a detailed, personalized career roadmap for:
- Current Role: {current_role}
- Target Role: {target_role}
- Experience Level: {experience or 'Not specified'}
- Current Skills: {skills or 'Not specified'}

Return ONLY a JSON object with this exact structure:
{{
  "timeline": "<total estimated timeline e.g. 6-9 months>",
  "overview": "<2-3 sentence summary of the journey>",
  "phases": [
    {{
      "phase": 1,
      "title": "<phase title>",
      "duration": "<e.g. 2 months>",
      "skills": ["<skill1>", "<skill2>", "<skill3>"],
      "resources": ["<resource1>", "<resource2>"],
      "milestone": "<what they should be able to do by end of phase>"
    }},
    {{
      "phase": 2,
      "title": "<phase title>",
      "duration": "<e.g. 2 months>",
      "skills": ["<skill1>", "<skill2>", "<skill3>"],
      "resources": ["<resource1>", "<resource2>"],
      "milestone": "<milestone>"
    }},
    {{
      "phase": 3,
      "title": "<phase title>",
      "duration": "<e.g. 2 months>",
      "skills": ["<skill1>", "<skill2>", "<skill3>"],
      "resources": ["<resource1>", "<resource2>"],
      "milestone": "<milestone>"
    }}
  ],
  "tips": ["<actionable tip1>", "<actionable tip2>", "<actionable tip3>"],
  "marketInsight": "<1-2 sentences about demand for target role in Arab market>"
}}
Return ONLY the JSON, no markdown.
"""
        try:
            result = ask_gemini(prompt)
            clean  = result.replace('```json', '').replace('```', '').strip()
            roadmap_data = json.loads(clean)

            # Save to DB
            saved = CareerRoadmap.objects.create(
                user=request.user,
                current_role=current_role,
                target_role=target_role,
                experience=experience,
                skills=skills,
                roadmap=roadmap_data,
            )

            return Response({
                'id':           saved.id,
                'current_role': saved.current_role,
                'target_role':  saved.target_role,
                'experience':   saved.experience,
                'skills':       saved.skills,
                'roadmap':      roadmap_data,
                'created_at':   saved.created_at.strftime('%Y-%m-%d'),
            }, status=201)

        except Exception as e:
            return Response({'error': str(e)}, status=500)


class CareerRoadmapDetailView(APIView):
    """
    GET    /api/ai/career-roadmap/<id>/  → retrieve specific roadmap
    DELETE /api/ai/career-roadmap/<id>/  → delete a roadmap
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            r = CareerRoadmap.objects.get(pk=pk, user=request.user)
        except CareerRoadmap.DoesNotExist:
            return Response({'error': 'Roadmap not found'}, status=404)

        return Response({
            'id':           r.id,
            'current_role': r.current_role,
            'target_role':  r.target_role,
            'experience':   r.experience,
            'skills':       r.skills,
            'roadmap':      r.roadmap,
            'created_at':   r.created_at.strftime('%Y-%m-%d'),
        })

    def delete(self, request, pk):
        try:
            r = CareerRoadmap.objects.get(pk=pk, user=request.user)
            r.delete()
            return Response({'detail': 'Roadmap deleted'}, status=204)
        except CareerRoadmap.DoesNotExist:
            return Response({'error': 'Roadmap not found'}, status=404)
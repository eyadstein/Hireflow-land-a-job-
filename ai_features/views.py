import os
import json
import google.generativeai as genai
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from .agent import HireBotAgent

GEMINI_KEY = os.environ.get('GEMINI_KEY', 'YOUR_GEMINI_KEY_HERE')
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

def ask_gemini(prompt):
    response = model.generate_content(prompt)
    return response.text

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
        

# Store agent sessions in memory (per user)
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

        # Get or create agent session for this user
        if reset or user_id not in agent_sessions:
            agent_sessions[user_id] = HireBotAgent()

        agent = agent_sessions[user_id]

        try:
            result = agent.run(message, user_context)
            return Response(result)
        except Exception as e:
            return Response({'error': str(e)}, status=500)
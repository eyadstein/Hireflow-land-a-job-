import os
import json
from google import genai
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.http import HttpResponse
from .agent import HireBotAgent
from .cv_generator import build_cv_pdf
from .models import (
    CareerRoadmap, CVProfile,
    MockInterviewSession, MockInterviewAnswer,
    LinkedInOptimization,
)

GEMINI_KEY = os.environ.get('GEMINI_KEY', 'YOUR_GEMINI_KEY_HERE')
client = genai.Client(api_key=GEMINI_KEY)


def ask_gemini(prompt):
    return client.models.generate_content(
        model='gemini-2.0-flash',
        contents=prompt,
    ).text


class ResumeAnalyzerView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        resume_text     = request.data.get('resume_text', '')
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
            clean  = result.replace('```json', '').replace('```', '').strip()
            return Response(json.loads(clean))
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class CoverLetterView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        name            = request.data.get('name', '')
        job_title       = request.data.get('job_title', '')
        company         = request.data.get('company', '')
        skills          = request.data.get('skills', '')
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
        role             = request.data.get('role', '')
        country          = request.data.get('country', '')
        experience_years = request.data.get('experience_years', 0)
        skills           = request.data.get('skills', '')

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
            clean  = result.replace('```json', '').replace('```', '').strip()
            return Response(json.loads(clean))
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class InterviewCoachView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        role            = request.data.get('role', '')
        level           = request.data.get('level', 'Mid')
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
            clean  = result.replace('```json', '').replace('```', '').strip()
            return Response(json.loads(clean))
        except Exception as e:
            return Response({'error': str(e)}, status=500)


agent_sessions = {}

class AgentChatView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user_id      = request.user.id
        message      = request.data.get('message', '')
        user_context = request.data.get('context', '')
        reset        = request.data.get('reset', False)

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


class CareerRoadmapView(APIView):
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

Return ONLY a JSON object:
{{
  "timeline": "<total estimated timeline>",
  "overview": "<2-3 sentence summary>",
  "phases": [
    {{
      "phase": 1,
      "title": "<phase title>",
      "duration": "<e.g. 2 months>",
      "skills": ["<skill1>", "<skill2>", "<skill3>"],
      "resources": ["<resource1>", "<resource2>"],
      "milestone": "<what they achieve by end of phase>"
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
  "tips": ["<tip1>", "<tip2>", "<tip3>"],
  "marketInsight": "<1-2 sentences about Arab market demand>"
}}
Return ONLY the JSON, no markdown.
"""
        try:
            result       = ask_gemini(prompt)
            clean        = result.replace('```json', '').replace('```', '').strip()
            roadmap_data = json.loads(clean)

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


class CVBuilderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cvs = CVProfile.objects.filter(user=request.user)
        data = [
            {
                'id':           cv.id,
                'full_name':    cv.full_name,
                'title':        cv.title,
                'email':        cv.email,
                'created_at':   cv.created_at.strftime('%Y-%m-%d'),
                'download_url': f"/api/ai/cv/{cv.id}/download/",
            }
            for cv in cvs
        ]
        return Response(data)

    def post(self, request):
        data     = request.data
        required = ['full_name', 'email', 'title']

        for field in required:
            if not data.get(field):
                return Response({'error': f'{field} is required'}, status=400)

        enhance    = data.get('enhance_with_ai', True)
        summary    = data.get('summary', '')
        experience = data.get('experience', [])

        enhanced_summary    = ''
        enhanced_experience = []

        if enhance:
            try:
                if summary:
                    sum_prompt = f"""
You are a professional CV writer.
Rewrite this professional summary to be more impactful, concise, and ATS-friendly.
Keep it to 3-4 sentences max. Use strong action words.
Original: {summary}
Return ONLY the improved summary text, nothing else.
"""
                    enhanced_summary = ask_gemini(sum_prompt).strip()

                if experience:
                    exp_prompt = f"""
You are a professional CV writer.
Enhance these job experience descriptions to be more impactful using strong action verbs and quantifiable achievements where possible.
Return ONLY a JSON array with the same structure but improved descriptions.
Experience: {json.dumps(experience)}
Return ONLY the JSON array, no markdown.
"""
                    exp_result          = ask_gemini(exp_prompt)
                    exp_clean           = exp_result.replace('```json', '').replace('```', '').strip()
                    enhanced_experience = json.loads(exp_clean)

            except Exception:
                enhanced_summary    = summary
                enhanced_experience = experience

        cv = CVProfile.objects.create(
            user                = request.user,
            full_name           = data.get('full_name'),
            email               = data.get('email'),
            phone               = data.get('phone', ''),
            location            = data.get('location', ''),
            title               = data.get('title'),
            summary             = summary,
            experience          = experience,
            education           = data.get('education', []),
            skills              = data.get('skills', []),
            languages           = data.get('languages', []),
            enhanced_summary    = enhanced_summary,
            enhanced_experience = enhanced_experience,
        )

        return Response({
            'id':                  cv.id,
            'full_name':           cv.full_name,
            'title':               cv.title,
            'enhanced_summary':    cv.enhanced_summary,
            'enhanced_experience': cv.enhanced_experience,
            'download_url':        f"/api/ai/cv/{cv.id}/download/",
            'created_at':          cv.created_at.strftime('%Y-%m-%d'),
            'message':             'CV created! Use download_url to get the PDF.',
        }, status=201)


class CVDownloadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            cv = CVProfile.objects.get(pk=pk, user=request.user)
        except CVProfile.DoesNotExist:
            return Response({'error': 'CV not found'}, status=404)

        try:
            pdf_bytes = build_cv_pdf(cv)
            filename  = f"cv_{cv.full_name.replace(' ', '_')}.pdf"
            response  = HttpResponse(pdf_bytes, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class MockInterviewStartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        role            = request.data.get('role', '')
        level           = request.data.get('level', 'Mid')
        job_description = request.data.get('job_description', '')

        if not role:
            return Response({'error': 'role is required'}, status=400)

        prompt = f"""
You are an expert technical interviewer.
Generate a realistic mock interview for:
- Role: {role}
- Level: {level}
{f'- Job Description: {job_description}' if job_description else ''}

Return ONLY a JSON object:
{{
  "questions": [
    {{"id": 1, "question": "<technical question>", "type": "technical", "difficulty": "<Easy|Medium|Hard>"}},
    {{"id": 2, "question": "<technical question>", "type": "technical", "difficulty": "<Easy|Medium|Hard>"}},
    {{"id": 3, "question": "<technical question>", "type": "technical", "difficulty": "<Easy|Medium|Hard>"}},
    {{"id": 4, "question": "<behavioral question>", "type": "behavioral", "difficulty": "Medium"}},
    {{"id": 5, "question": "<behavioral question>", "type": "behavioral", "difficulty": "Medium"}}
  ]
}}
Return ONLY the JSON, no markdown.
"""
        try:
            result    = ask_gemini(prompt)
            clean     = result.replace('```json', '').replace('```', '').strip()
            data      = json.loads(clean)
            questions = data.get('questions', [])

            session = MockInterviewSession.objects.create(
                user=request.user,
                role=role,
                level=level,
                questions=questions,
            )

            return Response({
                'session_id': session.id,
                'role':       session.role,
                'level':      session.level,
                'questions':  questions,
                'message':    'Answer all questions and POST to /submit/ with session_id',
            }, status=201)

        except Exception as e:
            return Response({'error': str(e)}, status=500)


class MockInterviewSubmitView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        session_id = request.data.get('session_id')
        answers    = request.data.get('answers', [])

        if not session_id:
            return Response({'error': 'session_id is required'}, status=400)
        if not answers:
            return Response({'error': 'answers are required'}, status=400)

        try:
            session = MockInterviewSession.objects.get(
                pk=session_id, user=request.user
            )
        except MockInterviewSession.DoesNotExist:
            return Response({'error': 'Session not found'}, status=404)

        if session.completed:
            return Response({'error': 'Session already submitted'}, status=400)

        questions_map = {q['id']: q for q in session.questions}

        qa_pairs = []
        for ans in answers:
            qid   = ans.get('question_id')
            q_obj = questions_map.get(qid, {})
            qa_pairs.append({
                'question_id': qid,
                'question':    q_obj.get('question', ''),
                'type':        q_obj.get('type', 'technical'),
                'answer':      ans.get('answer', ''),
            })

        grade_prompt = f"""
You are an expert interviewer grading a mock interview for a {session.role} ({session.level} level) position.

Grade each answer and return ONLY a JSON object:
{{
  "overall_score": <0-100>,
  "overall_feedback": "<2-3 sentence overall assessment>",
  "results": [
    {{
      "question_id": <id>,
      "question": "<question text>",
      "type": "<technical|behavioral>",
      "user_answer": "<their answer>",
      "score": <0-100>,
      "grade": "<A+|A|B+|B|C+|C|D|F>",
      "feedback": "<specific constructive feedback>",
      "ideal_answer": "<what a great answer would include>"
    }}
  ]
}}

Questions and Answers to grade:
{json.dumps(qa_pairs, indent=2)}
Return ONLY the JSON, no markdown.
"""
        try:
            result      = ask_gemini(grade_prompt)
            clean       = result.replace('```json', '').replace('```', '').strip()
            graded_data = json.loads(clean)

            for r in graded_data.get('results', []):
                qid   = r.get('question_id')
                q_obj = questions_map.get(qid, {})
                MockInterviewAnswer.objects.create(
                    session       = session,
                    question      = r.get('question', q_obj.get('question', '')),
                    question_type = r.get('type', 'technical'),
                    user_answer   = r.get('user_answer', ''),
                    score         = r.get('score'),
                    grade         = r.get('grade', ''),
                    feedback      = r.get('feedback', ''),
                    ideal_answer  = r.get('ideal_answer', ''),
                )

            session.overall_score    = graded_data.get('overall_score')
            session.overall_feedback = graded_data.get('overall_feedback', '')
            session.completed        = True
            session.save()

            return Response({
                'session_id':       session.id,
                'role':             session.role,
                'level':            session.level,
                'overall_score':    session.overall_score,
                'overall_feedback': session.overall_feedback,
                'results':          graded_data.get('results', []),
            })

        except Exception as e:
            return Response({'error': str(e)}, status=500)


class MockInterviewHistoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        sessions = MockInterviewSession.objects.filter(user=request.user)
        data = [
            {
                'session_id':       s.id,
                'role':             s.role,
                'level':            s.level,
                'overall_score':    s.overall_score,
                'overall_feedback': s.overall_feedback,
                'completed':        s.completed,
                'created_at':       s.created_at.strftime('%Y-%m-%d'),
            }
            for s in sessions
        ]
        return Response(data)


class MockInterviewDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            session = MockInterviewSession.objects.get(pk=pk, user=request.user)
        except MockInterviewSession.DoesNotExist:
            return Response({'error': 'Session not found'}, status=404)

        answers = session.answers.all()
        return Response({
            'session_id':       session.id,
            'role':             session.role,
            'level':            session.level,
            'overall_score':    session.overall_score,
            'overall_feedback': session.overall_feedback,
            'completed':        session.completed,
            'created_at':       session.created_at.strftime('%Y-%m-%d'),
            'answers': [
                {
                    'question':     a.question,
                    'type':         a.question_type,
                    'your_answer':  a.user_answer,
                    'score':        a.score,
                    'grade':        a.grade,
                    'feedback':     a.feedback,
                    'ideal_answer': a.ideal_answer,
                }
                for a in answers
            ],
        })


class LinkedInOptimizerView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        optimizations = LinkedInOptimization.objects.filter(user=request.user)
        data = [
            {
                'id':            o.id,
                'target_role':   o.target_role,
                'profile_score': o.profile_score,
                'created_at':    o.created_at.strftime('%Y-%m-%d'),
            }
            for o in optimizations
        ]
        return Response(data)

    def post(self, request):
        headline    = request.data.get('headline', '')
        about       = request.data.get('about', '')
        experience  = request.data.get('experience', '')
        skills      = request.data.get('skills', [])
        target_role = request.data.get('target_role', '')

        if not any([headline, about, experience]):
            return Response(
                {'error': 'At least one of headline, about, or experience is required'},
                status=400
            )

        prompt = f"""
You are an expert LinkedIn profile optimizer specializing in the Arab world job market.
Analyze and optimize this LinkedIn profile:
- Headline: {headline or 'Not provided'}
- About: {about or 'Not provided'}
- Experience: {experience or 'Not provided'}
- Current Skills: {json.dumps(skills) if skills else 'Not provided'}
- Target Role: {target_role or 'Not specified'}

Return ONLY a JSON object:
{{
  "profile_score": <0-100>,
  "optimized": {{
    "headline": "<rewritten optimized headline>",
    "about": "<rewritten optimized about section>",
    "skills_to_add": ["<skill1>", "<skill2>", "<skill3>"],
    "skills_to_remove": ["<skill1>"],
    "sections": [
      {{
        "section": "Headline",
        "score": <0-100>,
        "issues": ["<issue1>", "<issue2>"],
        "suggestions": ["<suggestion1>", "<suggestion2>"]
      }},
      {{
        "section": "About",
        "score": <0-100>,
        "issues": ["<issue1>", "<issue2>"],
        "suggestions": ["<suggestion1>", "<suggestion2>"]
      }},
      {{
        "section": "Experience",
        "score": <0-100>,
        "issues": ["<issue1>"],
        "suggestions": ["<suggestion1>", "<suggestion2>"]
      }},
      {{
        "section": "Skills",
        "score": <0-100>,
        "issues": ["<issue1>"],
        "suggestions": ["<suggestion1>"]
      }}
    ],
    "keywords": ["<keyword1>", "<keyword2>", "<keyword3>", "<keyword4>", "<keyword5>"],
    "overall_tips": ["<tip1>", "<tip2>", "<tip3>"],
    "marketInsight": "<1-2 sentences about LinkedIn visibility for this role in Arab market>"
  }}
}}
Return ONLY the JSON, no markdown.
"""
        try:
            result = ask_gemini(prompt)
            clean  = result.replace('```json', '').replace('```', '').strip()
            data   = json.loads(clean)

            saved = LinkedInOptimization.objects.create(
                user          = request.user,
                headline      = headline,
                about         = about,
                experience    = experience,
                skills        = skills,
                target_role   = target_role,
                profile_score = data.get('profile_score'),
                optimized     = data.get('optimized', {}),
            )

            return Response({
                'id':            saved.id,
                'profile_score': saved.profile_score,
                'target_role':   saved.target_role,
                'optimized':     saved.optimized,
                'created_at':    saved.created_at.strftime('%Y-%m-%d'),
            }, status=201)

        except Exception as e:
            return Response({'error': str(e)}, status=500)


class LinkedInOptimizerDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            o = LinkedInOptimization.objects.get(pk=pk, user=request.user)
        except LinkedInOptimization.DoesNotExist:
            return Response({'error': 'Optimization not found'}, status=404)

        return Response({
            'id':            o.id,
            'headline':      o.headline,
            'about':         o.about,
            'experience':    o.experience,
            'skills':        o.skills,
            'target_role':   o.target_role,
            'profile_score': o.profile_score,
            'optimized':     o.optimized,
            'created_at':    o.created_at.strftime('%Y-%m-%d'),
        })
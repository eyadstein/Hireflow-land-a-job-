import os
import json
from google import genai

GEMINI_KEY = os.environ.get('GEMINI_KEY', 'YOUR_KEY_HERE')
client = genai.Client(api_key=GEMINI_KEY)

# Define tools the agent can use
tools = [
    {
        "name": "analyze_resume",
        "description": "Analyze a resume and return ATS score, strengths, weaknesses, and suggestions",
        "parameters": {
            "type": "object",
            "properties": {
                "resume_text": {"type": "string", "description": "The full resume text"},
                "job_description": {"type": "string", "description": "Optional job description to match against"}
            },
            "required": ["resume_text"]
        }
    },
    {
        "name": "generate_cover_letter",
        "description": "Generate a professional cover letter",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "job_title": {"type": "string"},
                "company": {"type": "string"},
                "skills": {"type": "string"},
                "job_description": {"type": "string"}
            },
            "required": ["name", "job_title", "company"]
        }
    },
    {
        "name": "estimate_salary",
        "description": "Estimate salary for a role in a specific Arab country",
        "parameters": {
            "type": "object",
            "properties": {
                "role": {"type": "string"},
                "country": {"type": "string"},
                "experience_years": {"type": "integer"},
                "skills": {"type": "string"}
            },
            "required": ["role", "country"]
        }
    },
    {
        "name": "generate_interview_questions",
        "description": "Generate interview questions and answers for a role",
        "parameters": {
            "type": "object",
            "properties": {
                "role": {"type": "string"},
                "level": {"type": "string"},
                "job_description": {"type": "string"}
            },
            "required": ["role"]
        }
    },
    {
        "name": "career_advice",
        "description": "Give personalized career advice, roadmaps, and tips",
        "parameters": {
            "type": "object",
            "properties": {
                "question": {"type": "string"},
                "user_background": {"type": "string"}
            },
            "required": ["question"]
        }
    }
]

# Tool execution functions
def execute_tool(tool_name, params):
    model = genai.GenerativeModel('gemini-2.0-flash')

    if tool_name == "analyze_resume":
        prompt = f"""Analyze this resume as an ATS expert. Return JSON:
{{
  "atsScore": <0-100>,
  "overallRating": "<Excellent|Good|Average|Poor>",
  "summary": "<assessment>",
  "strengths": ["<s1>", "<s2>", "<s3>"],
  "weaknesses": ["<w1>", "<w2>", "<w3>"],
  "missingKeywords": ["<k1>", "<k2>", "<k3>"],
  "suggestions": [{{"priority": "High", "tip": "<tip>"}}, {{"priority": "Medium", "tip": "<tip>"}}],
  "estimatedRole": "<role>",
  "experienceLevel": "<Junior|Mid|Senior>"
}}
Resume: {params.get('resume_text', '')}
{f"Job Description: {params.get('job_description', '')}" if params.get('job_description') else ''}
Return ONLY JSON."""
        result = client.models.generate_content(model='gemini-2.0-flash', contents=prompt).text
        try:
            return json.loads(result.replace('```json','').replace('```','').strip())
        except:
            return {"error": "Could not parse result"}

    elif tool_name == "generate_cover_letter":
        prompt = f"""Write a professional cover letter for {params.get('name')} applying for {params.get('job_title')} at {params.get('company')}.
Skills: {params.get('skills', 'Not specified')}
Job Description: {params.get('job_description', 'Not specified')}
Write 3-4 paragraphs. Professional tone. Return ONLY the letter."""
        return {"cover_letter": client.models.generate_content(model='gemini-2.0-flash', contents=prompt).text}

    elif tool_name == "estimate_salary":
        prompt = f"""Estimate salary for {params.get('role')} in {params.get('country')} with {params.get('experience_years', 0)} years experience.
Return ONLY JSON:
{{
  "minSalary": <USD/month>,
  "maxSalary": <USD/month>,
  "avgSalary": <USD/month>,
  "currency": "<local>",
  "minLocal": <local/month>,
  "maxLocal": <local/month>,
  "marketDemand": "<High|Medium|Low>",
  "topSkills": ["<s1>", "<s2>", "<s3>"],
  "insight": "<market insight>"
}}"""
        result = client.models.generate_content(model='gemini-2.0-flash', contents=prompt).text
        try:
            return json.loads(result.replace('```json','').replace('```','').strip())
        except:
            return {"error": "Could not parse result"}

    elif tool_name == "generate_interview_questions":
        prompt = f"""Generate interview questions for {params.get('role')} ({params.get('level', 'Mid')} level).
Return ONLY JSON:
{{
  "technical": [{{"question": "<q>", "answer": "<a>", "difficulty": "<Easy|Medium|Hard>"}}],
  "behavioral": [{{"question": "<q>", "answer": "<a>"}}],
  "tips": ["<tip1>", "<tip2>", "<tip3>"]
}}"""
        result = client.models.generate_content(model='gemini-2.0-flash', contents=prompt).text
        try:
            return json.loads(result.replace('```json','').replace('```','').strip())
        except:
            return {"error": "Could not parse result"}

    elif tool_name == "career_advice":
        prompt = f"""You are an expert career coach for the Arab world job market.
User background: {params.get('user_background', 'Not specified')}
Question: {params.get('question')}
Give detailed, actionable career advice. Be specific and encouraging."""
        return {"advice": client.models.generate_content(model='gemini-2.0-flash', contents=prompt).text}
    return {"error": f"Unknown tool: {tool_name}"}


class HireBotAgent:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        self.conversation_history = []

    def run(self, user_message, user_context=""):
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # Step 1 - Decide which tool to use
        decision_prompt = f"""You are HireBot, an AI career assistant for the Arab world job market.

Available tools:
{json.dumps([{"name": t["name"], "description": t["description"]} for t in tools], indent=2)}

User context: {user_context}
Conversation so far: {json.dumps(self.conversation_history[-6:], indent=2)}
Latest message: {user_message}

Decide if you need a tool. Return ONLY JSON:
{{
  "needsTool": <true|false>,
  "toolName": "<tool name or null>",
  "toolParams": {{<params or empty>}},
  "directResponse": "<if no tool needed, respond here, else null>"
}}"""

        decision_text = self.model.generate_content(decision_prompt).text
        try:
            decision = json.loads(decision_text.replace('```json','').replace('```','').strip())
        except:
            return {"response": decision_text, "toolUsed": None, "toolResult": None}

        # Step 2 - Execute tool if needed
        tool_result = None
        if decision.get("needsTool") and decision.get("toolName"):
            tool_result = execute_tool(decision["toolName"], decision.get("toolParams", {}))

            # Step 3 - Generate final response using tool result
            final_prompt = f"""You are HireBot, an AI career assistant.
User asked: {user_message}
Tool used: {decision["toolName"]}
Tool result: {json.dumps(tool_result, indent=2)}

Now give a friendly, helpful response to the user based on the tool result.
Be conversational, clear and encouraging. Format nicely."""

            final_response = self.model.generate_content(final_prompt).text
        else:
            final_response = decision.get("directResponse") or "I'm here to help with your career!"

        self.conversation_history.append({
            "role": "assistant",
            "content": final_response
        })

        return {
            "response": final_response,
            "toolUsed": decision.get("toolName"),
            "toolResult": tool_result
        }
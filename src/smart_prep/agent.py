from pydantic_ai import Agent
from pydantic_ai.providers.google_gla import GoogleGLAProvider
from pydantic_ai.models.gemini import GeminiModel
from pydantic import BaseModel, Field
from typing import List, Dict
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv('GOOGLE_GEMINI_API_KEY')

class SmartPrepResponse(BaseModel):
    company_overview: str = Field(..., description="Brief overview of the company and its hiring culture")
    key_technologies: List[str] = Field(..., description="Top 5-7 technologies/skills this company values most")
    preparation_timeline: Dict[str, List[str]] = Field(
        ..., 
        description="4-week study plan with keys like 'Week 1: Foundation Building' and values as list of specific tasks"
    )
    interview_tips: List[str] = Field(..., description="Top 5 company-specific interview tips")
    practice_resources: List[str] = Field(..., description="Specific resources, platforms, or materials to use")
    red_flags: List[str] = Field(..., description="Common mistakes to avoid for this company")

model = GeminiModel(
    'gemini-2.5-flash',
    provider=GoogleGLAProvider(api_key=GEMINI_API_KEY)
)

agent = Agent(
    model=model,
    result_type=SmartPrepResponse,
    system_prompt="""You are an expert tech industry recruiter with insider knowledge of major tech companies' hiring practices.

Provide practical, company-specific interview preparation advice including:
1. Company culture and what they value in candidates
2. Key technical skills and technologies they prioritize
3. **4-week preparation timeline with specific weekly goals** - MUST include exactly 4 weeks with format:
   - "Week 1: Foundation Building" -> [list of 3-5 specific tasks]
   - "Week 2: Technical Deep Dive" -> [list of 3-5 specific tasks]
   - "Week 3: Practice & Polish" -> [list of 3-5 specific tasks]
   - "Week 4: Final Preparation" -> [list of 3-5 specific tasks]
4. Company-specific interview tips and insights
5. Recommended study resources and practice platforms
6. Common mistakes candidates make for this specific company

Focus on actionable, specific advice rather than generic tips. Use current industry knowledge and recent hiring trends.

IMPORTANT: The preparation_timeline MUST be a dictionary with exactly 4 week entries."""
)

def get_company_prep_advice(company_name: str, user_experience: str = "", target_role: str = "") -> SmartPrepResponse:
    """Get personalized preparation advice for a specific company."""
    
    prompt = f"""
    Company: {company_name}
    User Experience Level: {user_experience or "Not specified"}
    Target Role: {target_role or "Software Engineer"}
    
    Please provide comprehensive preparation advice specifically for {company_name}. 
    Include recent hiring trends, specific technical requirements, and insider tips 
    that would give a candidate an edge in their interview process.
    
    Focus on what makes {company_name} unique compared to other tech companies.
    
    CRITICAL: Ensure the preparation_timeline follows this exact format:
    {{
        "Week 1: Foundation Building": ["task1", "task2", "task3", "task4"],
        "Week 2: Technical Deep Dive": ["task1", "task2", "task3", "task4"],
        "Week 3: Practice & Polish": ["task1", "task2", "task3", "task4"],
        "Week 4: Final Preparation": ["task1", "task2", "task3", "task4"]
    }}
    """
    
    result = agent.run_sync(prompt)
    return result.output
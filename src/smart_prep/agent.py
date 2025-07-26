from pydantic_ai import Agent
from pydantic_ai.providers.google_gla import GoogleGLAProvider
from pydantic_ai.models.gemini import GeminiModel
from pydantic import BaseModel, Field
from typing import List, Dict
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv('GOOGLE_GEMINI_API_KEY')

class PreparationTimeline(BaseModel):
    """4-week preparation timeline with explicit fields for Gemini compatibility"""
    week_1_foundation_building: List[str] = Field(
        ..., 
        description="Week 1: Foundation Building - List of 3-5 specific foundational tasks like company research, basic concept review"
    )
    week_2_technical_deep_dive: List[str] = Field(
        ..., 
        description="Week 2: Technical Deep Dive - List of 3-5 advanced technical preparation tasks like algorithms, system design"
    )
    week_3_practice_and_polish: List[str] = Field(
        ..., 
        description="Week 3: Practice & Polish - List of 3-5 interview practice tasks like mock interviews, behavioral prep"
    )
    week_4_final_preparation: List[str] = Field(
        ..., 
        description="Week 4: Final Preparation - List of 3-5 final preparation tasks like review, question prep, confidence building"
    )
    
    def to_dict(self) -> Dict[str, List[str]]:
        """Convert to dictionary format for database storage"""
        return {
            "Week 1: Foundation Building": self.week_1_foundation_building,
            "Week 2: Technical Deep Dive": self.week_2_technical_deep_dive,
            "Week 3: Practice & Polish": self.week_3_practice_and_polish,
            "Week 4: Final Preparation": self.week_4_final_preparation
        }

class SmartPrepResponse(BaseModel):
    company_overview: str = Field(..., description="Brief overview of the company and its hiring culture")
    key_technologies: List[str] = Field(..., description="Top 5-7 technologies/skills this company values most")
    preparation_timeline: PreparationTimeline = Field(
        ..., 
        description="4-week structured preparation timeline with specific weekly goals"
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

Provide practical, company-specific interview preparation advice. 

IMPORTANT FORMATTING RULES:
- Write in clear, professional prose without markdown formatting
- Use complete sentences and paragraphs
- Avoid using ** for bold or # for headers
- Write naturally as if speaking to a candidate
- Keep each tip, resource, or red flag as a single, clear sentence

Provide:
1. Company culture and what they value in candidates
2. Key technical skills and technologies they prioritize
3. 4-week preparation timeline with specific weekly goals
4. Company-specific interview tips and insights
5. Recommended study resources and practice platforms
6. Common mistakes candidates make for this specific company

Focus on actionable, specific advice rather than generic tips."""
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
    
    For the preparation timeline, provide:
    - Week 1 (Foundation Building): Focus on {company_name} research, culture understanding, basic technical review
    - Week 2 (Technical Deep Dive): Advanced technical skills, algorithms, system design relevant to {company_name}
    - Week 3 (Practice & Polish): Mock interviews, behavioral preparation, communication skills
    - Week 4 (Final Preparation): Final review, thoughtful questions, confidence building
    
    Each week should have 3-5 specific, actionable tasks tailored to {company_name}.
    """
    
    
    result = agent.run_sync(prompt)
    return result.output
import os
import PyPDF2
import docx
import io
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider
from pydantic import BaseModel, Field
from typing import List

load_dotenv()

GEMINI_API_KEY = os.getenv('GOOGLE_GEMINI_API_KEY')

class ResumeResponse(BaseModel):
    overall_score: int = Field(..., ge=1, le=100, description="Overall resume quality score from 1-100")
    strengths: List[str] = Field(..., description="Top 3 strongest aspects of the resume")
    improvement_areas: List[str] = Field(..., description="Top 3 areas that need improvement")
    ats_score: int = Field(..., ge=1, le=100, description="ATS (Applicant Tracking System) compatibility score from 1-100")
    missing_elements: List[str] = Field(..., description="Key sections or information missing from the resume")
    recommendations: List[str] = Field(..., description="Specific actionable recommendations for improvement")

model = GeminiModel(
    'gemini-2.5-flash',
    provider=GoogleGLAProvider(api_key=GEMINI_API_KEY)
)

agent = Agent(
    model=model,
    result_type=ResumeResponse,
    system_prompt="""You are an expert resume analyzer with 15+ years of experience in technical recruitment. 

Analyze resumes and provide:
1. Overall score (1-100) - must be between 1 and 100
2. Top 3 strengths 
3. Top 3 areas for improvement
4. ATS compatibility score (1-100) - must be between 1 and 100
5. Key missing elements
6. Specific actionable recommendations

Be direct, constructive, and focus on technical roles. Ensure scores are realistic and within the 1-100 range."""
)

def read_document(file_content: bytes, file_name: str) -> str:
    """Extract text from PDF, DOCX, or TXT files."""
    try:
        if file_name.lower().endswith('.pdf'):
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            return "\n".join([page.extract_text() for page in pdf_reader.pages])
        
        elif file_name.lower().endswith(('.docx', '.doc')):
            doc = docx.Document(io.BytesIO(file_content))
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
        
        else:  # Text files
            return file_content.decode('utf-8', errors='ignore')
    
    except Exception as e:
        return f"Error reading file: {str(e)}"

def analyze_resume(file_content: bytes, file_name: str, target_role: str = "") -> ResumeResponse:
    """Analyze a resume and return structured feedback."""
    # Extract text from document first
    resume_text = read_document(file_content, file_name)
    
    # Create the prompt with the extracted text
    prompt = f"""
    Target Role: {target_role or "General technical position"}
    
    Resume Content:
    {resume_text}
    
    Please analyze this resume and provide detailed feedback with scores between 1-100.
    """
    
    # Run the agent with the prompt
    result = agent.run_sync(prompt)
    return result.data
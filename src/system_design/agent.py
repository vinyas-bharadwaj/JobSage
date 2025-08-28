import json
from pydantic_ai import Agent, BinaryContent
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider
from pydantic import BaseModel, Field
from typing import List
from django.conf import settings


GEMINI_API_KEY = settings.GEMINI_API_KEY

class SystemDesignResponse(BaseModel):
    overall_score: int = Field(..., ge=1, le=100, description="Overall system design quality score from 1-100")
    scalability_score: int = Field(..., ge=1, le=100, description="How well the design handles scale from 1-100")
    reliability_score: int = Field(..., ge=1, le=100, description="System reliability and fault tolerance score from 1-100")
    strengths: List[str] = Field(..., description="Top 3 strongest aspects of the design")
    weaknesses: List[str] = Field(..., description="Top 3 areas that need improvement")
    missing_components: List[str] = Field(..., description="Critical components or considerations that are missing")
    recommendations: List[str] = Field(..., description="Specific actionable recommendations for improvement")

model = GeminiModel(
    'gemini-2.5-flash',
    provider=GoogleGLAProvider(api_key=GEMINI_API_KEY)
)

agent = Agent(
    model=model,
    result_type=SystemDesignResponse,
    system_prompt="""You are a senior system design interviewer with 10+ years of experience at major tech companies (Google, Amazon, Meta, Netflix).

Analyze system design diagrams from images and provide:
1. Overall score (1-100) - must be between 1 and 100
2. Scalability score (1-100) - how well it handles scale
3. Reliability score (1-100) - fault tolerance and redundancy
4. Top 3 strengths of the design
5. Top 3 areas that need improvement  
6. Missing critical components
7. Specific actionable recommendations

Focus on:
- Component architecture and relationships
- Data flow and communication patterns
- Scalability considerations (load balancing, caching, sharding)
- Reliability patterns (redundancy, failover, monitoring)
- Appropriate technology choices
- Security considerations
- Performance optimizations

Be direct, constructive, and provide feedback similar to actual FAANG interviews. 
Analyze the visual diagram carefully and identify all components, connections, and architectural patterns."""
)

def analyze_system_design(image_data: bytes, problem_statement: str = "", requirements: str = "") -> SystemDesignResponse:
    """Analyze a system design diagram from an image and return structured feedback."""
    
    # Create the prompt
    prompt = f"""
    Problem Statement: {problem_statement or "General system design evaluation"}
    
    Requirements: {requirements or "Standard scalability, reliability, and performance requirements"}
    
    Please analyze the system design diagram in the provided image. Look for:
    
    1. **Architecture Components**: Identify all services, databases, caches, load balancers, etc.
    2. **Data Flow**: How data moves through the system
    3. **Scalability**: How the system handles increased load
    4. **Reliability**: Fault tolerance and backup mechanisms
    5. **Technology Choices**: Appropriateness of selected technologies
    6. **Missing Elements**: What critical components might be missing
    
    Provide detailed feedback with scores between 1-100 for overall quality, scalability, and reliability.
    """
    
    try:
        # Run the agent with the image
        result = agent.run_sync([
            prompt,
            BinaryContent(data=image_data, media_type='image/png')
        ])
        
        return result.data
    except Exception as e:
        pass
import os
import json
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider
from pydantic import BaseModel, Field
from typing import List

load_dotenv()

GEMINI_API_KEY = os.getenv('GOOGLE_GEMINI_API_KEY')

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

Analyze system design diagrams and provide:
1. Overall score (1-100) - must be between 1 and 100
2. Scalability score (1-100) - how well it handles scale
3. Reliability score (1-100) - fault tolerance and redundancy
4. Top 3 strengths of the design
5. Top 3 areas that need improvement  
6. Missing critical components
7. Specific actionable recommendations

Focus on scalability, reliability, appropriate component selection, and industry best practices. 
Be direct, constructive, and provide feedback similar to actual FAANG interviews."""
)

def parse_excalidraw_diagram(excalidraw_data: str) -> str:
    """Extract readable information from Excalidraw diagram data."""
    try:
        if isinstance(excalidraw_data, str):
            diagram_data = json.loads(excalidraw_data)
        else:
            diagram_data = excalidraw_data
        
        # Extract text elements (component names, labels)
        text_elements = []
        components_count = 0
        connections_count = 0
        
        for element in diagram_data.get('elements', []):
            if element.get('type') == 'text' and element.get('text'):
                text_elements.append(element.get('text'))
            elif element.get('type') in ['rectangle', 'ellipse', 'diamond']:
                components_count += 1
            elif element.get('type') in ['arrow', 'line']:
                connections_count += 1
        
        return f"""
        Diagram Components: {components_count} components, {connections_count} connections
        
        Text Labels Found:
        {chr(10).join([f"- {text}" for text in text_elements if text])}
        """
        
    except Exception as e:
        return f"Error parsing diagram: {str(e)}. Analyzing based on provided description."

def analyze_system_design(excalidraw_data: str, problem_statement: str = "", requirements: str = "") -> SystemDesignResponse:
    """Analyze a system design diagram and return structured feedback."""
    # Parse the diagram data
    diagram_description = parse_excalidraw_diagram(excalidraw_data)
    
    # Create the prompt
    prompt = f"""
    Problem: {problem_statement or "General system design evaluation"}
    
    Requirements: {requirements or "Standard scalability, reliability, and performance requirements"}
    
    System Design Diagram:
    {diagram_description}
    
    Raw Diagram Data (sample):
    {str(excalidraw_data)[:500]}...
    
    Please analyze this system design and provide detailed feedback with scores between 1-100.
    """
    
    # Run the agent
    result = agent.run_sync(prompt)
    return result.output
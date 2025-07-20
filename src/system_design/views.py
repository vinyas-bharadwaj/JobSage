from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .agent import analyze_system_design

def system_design_page(request):
    return render(request, 'system_design/system_design-page.html', context={})

@csrf_exempt
@require_http_methods(["POST"])
def analyze_system_design_view(request):
    try:
        data = json.loads(request.body)
        
        # Extract the diagram data
        excalidraw_data = {
            'elements': data.get('elements', []),
            'appState': data.get('appState', {})
        }
        
        question = data.get('question', '')
        requirements = data.get('requirements', '')
        
        # Analyze the design
        analysis = analyze_system_design(
            excalidraw_data=json.dumps(excalidraw_data),
            problem_statement=question,
            requirements=requirements
        )
        
        # Convert Pydantic model to dict for JSON response
        analysis_dict = {
            'overall_score': analysis.overall_score,
            'scalability_score': analysis.scalability_score,
            'reliability_score': analysis.reliability_score,
            'strengths': analysis.strengths,
            'weaknesses': analysis.weaknesses,
            'missing_components': analysis.missing_components,
            'recommendations': analysis.recommendations
        }
        
        return JsonResponse({
            'success': True,
            'analysis': analysis_dict
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
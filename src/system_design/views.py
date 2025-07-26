from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
import json
from .agent import analyze_system_design
from .models import SystemDesignQuestion

def system_design_page(request):
    questions = SystemDesignQuestion.objects.all()
    context = {
        'questions': questions,
        'total_questions': SystemDesignQuestion.objects.count()
    }

    return render(request, 'system_design/system_design-page.html', context=context)


@login_required
@require_http_methods(["POST"])
def add_question(request):
    """Add new system design question"""
    try:
        data = json.loads(request.body)
        print(f"Received data: {data}")  # Debug log
        
        # Validate required fields
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        
        if not title or not description:
            return JsonResponse({
                'success': False,
                'error': 'Title and description are required'
            }, status=400)
        
        question = SystemDesignQuestion.objects.create(
            title=title,
            description=description,
            company=data.get('company', '').strip(),
            difficulty=data.get('difficulty', 'Medium'),
            published_by=request.user
        )
        
        print(f"Question created with ID: {question.id}")  # Debug log
        
        return JsonResponse({
            'success': True,
            'message': 'Question added successfully!',
            'question_id': question.id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        print(f"Error creating question: {str(e)}")  # Debug log
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


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
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
import json
from .agent import analyze_system_design
from .models import SystemDesignQuestion, SystemDesignSubmission
from .forms import SystemDesignQuestionForm, SystemDesignSubmissionForm

def system_design_page(request):
    """Main system design page with questions list"""
    questions = SystemDesignQuestion.objects.all().order_by('-created_at')[:12]
    form = SystemDesignQuestionForm()
    
    # Handle form submission
    if request.method == 'POST' and request.user.is_authenticated:
        form = SystemDesignQuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.published_by = request.user
            question.save()
            messages.success(request, 'Question added successfully!')
            return redirect('system-design-page')  # Changed this line
        else:
            messages.error(request, 'Please correct the errors below.')
    
    context = {
        'questions': questions,
        'total_questions': SystemDesignQuestion.objects.count(),
        'form': form,
    }
    
    return render(request, 'system_design/system_design-page.html', context)

def design_question_view(request, question_id):
    """View to work on a specific design question"""
    question = get_object_or_404(SystemDesignQuestion, id=question_id)
    
    # Check if user already has a submission
    existing_submission = None
    if request.user.is_authenticated:
        try:
            existing_submission = SystemDesignSubmission.objects.get(
                question=question, 
                user=request.user
            )
        except SystemDesignSubmission.DoesNotExist:
            pass
    
    context = {
        'question': question,
        'existing_submission': existing_submission,
    }
    
    return render(request, 'system_design/design_question.html', context)

@login_required
def submit_design_view(request, question_id):
    """Handle design submission and analysis"""
    question = get_object_or_404(SystemDesignQuestion, id=question_id)
    
    if request.method == 'POST':
        form = SystemDesignSubmissionForm(request.POST)
        
        if form.is_valid():
            try:
                # Get or create submission
                submission, created = SystemDesignSubmission.objects.get_or_create(
                    question=question,
                    user=request.user,
                    defaults={
                        'design_data': {},
                        'analysis_completed': False
                    }
                )
                
                # Parse the design data
                elements = json.loads(form.cleaned_data['excalidraw_elements'])
                app_state = json.loads(form.cleaned_data.get('excalidraw_app_state', '{}'))
                
                # Save design data
                submission.save_design_data(elements, app_state)
                submission.save()
                
                # Analyze the design
                excalidraw_data = json.dumps({
                    'elements': elements,
                    'appState': app_state
                })
                
                analysis = analyze_system_design(
                    excalidraw_data=excalidraw_data,
                    problem_statement=question.title,
                    requirements=question.description
                )
                
                # Save analysis results
                submission.overall_score = analysis.overall_score
                submission.scalability_score = analysis.scalability_score
                submission.reliability_score = analysis.reliability_score
                submission.strengths = analysis.strengths
                submission.weaknesses = analysis.weaknesses
                submission.missing_components = analysis.missing_components
                submission.recommendations = analysis.recommendations
                submission.analysis_completed = True
                submission.save()
                
                messages.success(request, 'Design submitted and analyzed successfully!')
                return redirect('design-results', submission_id=submission.id)
                
            except Exception as e:
                messages.error(request, f'Error analyzing design: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors in your submission.')
    
    return redirect('design-question', question_id=question_id)

def design_results_view(request, submission_id):
    """View to display analysis results"""
    submission = get_object_or_404(SystemDesignSubmission, id=submission_id)
    
    # Check if user can view this submission
    if request.user != submission.user and not request.user.is_staff:
        messages.error(request, 'You can only view your own submissions.')
        return redirect('system-design')
    
    context = {
        'submission': submission,
        'question': submission.question,
    }
    
    return render(request, 'system_design/design_results.html', context)

def user_submissions_view(request):
    """View user's design submissions"""
    if not request.user.is_authenticated:
        return redirect('login-page')  # Make sure this matches your URL name
    
    submissions = SystemDesignSubmission.objects.filter(
        user=request.user
    ).select_related('question').order_by('-created_at')
    
    context = {
        'submissions': submissions,
    }
    
    return render(request, 'system_design/user_submissions.html', context)
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
import json
import base64
import io
import traceback
from PIL import Image
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
            question.created_by = request.user  
            question.save()
            messages.success(request, 'Question added successfully!')
            return redirect('system-design-page')
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
    
    # Get all submissions for this question by the current user
    user_submissions = []
    if request.user.is_authenticated:
        user_submissions = SystemDesignSubmission.objects.filter(
            question=question, 
            user=request.user
        ).order_by('-created_at')
    
    context = {
        'question': question,
        'user_submissions': user_submissions,
    }
    
    return render(request, 'system_design/design_question.html', context)

@login_required
def submit_design_view(request, question_id):
    """Handle design submission and analysis"""
    question = get_object_or_404(SystemDesignQuestion, id=question_id)
    
    if request.method == 'POST':
        try:
            # Handle file upload
            uploaded_file = request.FILES.get('uploaded_design')
            if not uploaded_file:
                messages.error(request, 'No file uploaded. Please select a design image.')
                return redirect('design-question', question_id=question_id)
            
            print(f"Uploaded file: {uploaded_file.name}, size: {uploaded_file.size}")
            
            # Validate file type
            if not uploaded_file.content_type.startswith('image/'):
                messages.error(request, 'Please upload a valid image file.')
                return redirect('design-question', question_id=question_id)
            
            # Validate file size (10MB limit)
            if uploaded_file.size > 10 * 1024 * 1024:
                messages.error(request, 'File size must be less than 10MB.')
                return redirect('design-question', question_id=question_id)
            
            # Create a new submission with the uploaded file
            submission = SystemDesignSubmission.objects.create(
                question=question,
                user=request.user,
                design_image=uploaded_file,
                analysis_completed=False
            )
            
            print(f"New submission created with ID: {submission.id}")
            
            # Analyze the design using the image file
            try:
                print("Starting design analysis...")
                
                # Read the image file for analysis
                with submission.design_image.open('rb') as image_file:
                    image_bytes = image_file.read()
                
                analysis = analyze_system_design(
                    image_data=image_bytes,
                    problem_statement=question.title,
                    requirements=question.description
                )
                
                print(f"Analysis completed: {analysis}")
                
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
                
                print("Analysis results saved successfully")
                
                messages.success(request, 'Design submitted and analyzed successfully!')
                return redirect('design-results', submission_id=submission.id)
                
            except Exception as analysis_error:
                print(f"Analysis error: {analysis_error}")
                print(f"Traceback: {traceback.format_exc()}")
                
                # Save a fallback submission
                submission.overall_score = 50
                submission.scalability_score = 50
                submission.reliability_score = 50
                submission.strengths = ["Design uploaded successfully"]
                submission.weaknesses = ["Analysis encountered an error"]
                submission.missing_components = ["Unable to analyze due to processing error"]
                submission.recommendations = [f"Analysis error: {str(analysis_error)}", "Please try again or contact support"]
                submission.analysis_completed = True
                submission.save()
                
                messages.warning(request, 'Design submitted but analysis encountered an issue. Please check the results.')
                return redirect('design-results', submission_id=submission.id)
            
        except Exception as e:
            print(f"General error: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            messages.error(request, f'Error processing submission: {str(e)}')
    
    return redirect('design-question', question_id=question_id)

def design_results_view(request, submission_id):
    """View to display analysis results"""
    submission = get_object_or_404(SystemDesignSubmission, id=submission_id)
    
    # Check if user can view this submission
    if request.user != submission.user and not request.user.is_staff:
        messages.error(request, 'You can only view your own submissions.')
        return redirect('system-design-page')
    
    print(f"Displaying results for submission {submission_id}")  # Debug
    print(f"Analysis completed: {submission.analysis_completed}")  # Debug
    print(f"Overall score: {submission.overall_score}")  # Debug
    
    context = {
        'submission': submission,
        'question': submission.question,
    }
    
    return render(request, 'system_design/design_results.html', context)

def user_submissions_view(request):
    """View user's design submissions"""
    if not request.user.is_authenticated:
        return redirect('login-page')
    
    submissions = SystemDesignSubmission.objects.filter(
        user=request.user
    ).select_related('question').order_by('-created_at')
    
    # Calculate average score for completed analyses
    completed_submissions = submissions.filter(analysis_completed=True)
    avg_score = None
    if completed_submissions.exists():
        total_score = sum(s.overall_score for s in completed_submissions if s.overall_score)
        count = completed_submissions.filter(overall_score__isnull=False).count()
        if count > 0:
            avg_score = total_score / count
    
    # Group submissions by question for better display
    from collections import defaultdict
    submissions_by_question = defaultdict(list)
    for submission in submissions:
        submissions_by_question[submission.question].append(submission)
    
    context = {
        'submissions': submissions,
        'submissions_by_question': dict(submissions_by_question),
        'avg_score': avg_score,
        'total_submissions': submissions.count(),
    }
    
    return render(request, 'system_design/user_submissions.html', context)
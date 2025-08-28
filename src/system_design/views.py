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
            question.created_by = request.user  # Fixed field name
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
        try:
            submission_type = request.POST.get('submission_type', 'canvas')
            image_bytes = None
            
            print(f"Processing submission type: {submission_type}")  # Debug
            
            if submission_type == 'upload':
                # Handle file upload
                uploaded_file = request.FILES.get('uploaded_design')
                if not uploaded_file:
                    messages.error(request, 'No file uploaded. Please select a design image.')
                    return redirect('design-question', question_id=question_id)
                
                print(f"Uploaded file: {uploaded_file.name}, size: {uploaded_file.size}")  # Debug
                
                # Validate file type
                if not uploaded_file.content_type.startswith('image/'):
                    messages.error(request, 'Please upload a valid image file.')
                    return redirect('design-question', question_id=question_id)
                
                # Validate file size (10MB limit)
                if uploaded_file.size > 10 * 1024 * 1024:
                    messages.error(request, 'File size must be less than 10MB.')
                    return redirect('design-question', question_id=question_id)
                
                # Read the uploaded file
                image_bytes = uploaded_file.read()
                
                # Validate and convert image if needed
                try:
                    img = Image.open(io.BytesIO(image_bytes))
                    print(f"Image format: {img.format}, size: {img.size}")  # Debug
                    if img.format not in ['PNG', 'JPEG', 'JPG']:
                        # Convert to PNG
                        png_buffer = io.BytesIO()
                        img.save(png_buffer, format='PNG')
                        image_bytes = png_buffer.getvalue()
                        print("Converted image to PNG")  # Debug
                except Exception as e:
                    print(f"Image processing error: {e}")  # Debug
                    messages.error(request, 'Invalid image format. Please try again.')
                    return redirect('design-question', question_id=question_id)
                    
            else:
                # Handle canvas capture
                design_image_data = request.POST.get('design_image')
                if not design_image_data:
                    messages.error(request, 'No design image provided. Please create a design and try again.')
                    return redirect('design-question', question_id=question_id)
                
                print(f"Canvas data length: {len(design_image_data)}")  # Debug
                
                # Parse base64 image data
                if design_image_data.startswith('data:image'):
                    # Remove data URL prefix
                    header, image_data = design_image_data.split(',', 1)
                    image_bytes = base64.b64decode(image_data)
                else:
                    # Assume it's already base64 encoded
                    image_bytes = base64.b64decode(design_image_data)
                
                # Validate image
                try:
                    img = Image.open(io.BytesIO(image_bytes))
                    print(f"Canvas image format: {img.format}, size: {img.size}")  # Debug
                    # Convert to PNG if needed
                    if img.format != 'PNG':
                        png_buffer = io.BytesIO()
                        img.save(png_buffer, format='PNG')
                        image_bytes = png_buffer.getvalue()
                except Exception as e:
                    print(f"Canvas image processing error: {e}")  # Debug
                    messages.error(request, 'Invalid image format. Please try again.')
                    return redirect('design-question', question_id=question_id)
            
            # Get or create submission
            submission, created = SystemDesignSubmission.objects.get_or_create(
                question=question,
                user=request.user,
                defaults={
                    'design_data': {},
                    'analysis_completed': False
                }
            )
            
            print(f"Submission created/retrieved: {created}")  # Debug
            
            # Save design metadata
            submission.design_data = {
                'submission_type': submission_type,
                'timestamp': str(submission.created_at),
                'image_provided': True
            }
            submission.save()
            
            # Analyze the design using the image
            try:
                print("Starting design analysis...")  # Debug
                analysis = analyze_system_design(
                    image_data=image_bytes,
                    problem_statement=question.title,
                    requirements=question.description
                )
                
                print(f"Analysis completed: {analysis}")  # Debug
                
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
                
                print("Analysis results saved successfully")  # Debug
                
                messages.success(request, 'Design submitted and analyzed successfully!')
                return redirect('design-results', submission_id=submission.id)
                
            except Exception as analysis_error:
                print(f"Analysis error: {analysis_error}")  # Debug
                print(f"Traceback: {traceback.format_exc()}")  # Debug
                
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
            print(f"General error: {e}")  # Debug
            print(f"Traceback: {traceback.format_exc()}")  # Debug
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
    
    context = {
        'submissions': submissions,
    }
    
    return render(request, 'system_design/user_submissions.html', context)
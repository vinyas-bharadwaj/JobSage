from django.shortcuts import render
from django.contrib import messages
from django.http import JsonResponse
from .agent import analyze_resume
import json

# Create your views here.
def resume_page(request):
    context = {}
    
    if request.method == 'POST':
        # Check if file was uploaded
        if 'resume_file' not in request.FILES:
            messages.error(request, 'Please select a resume file to upload.')
            return render(request, 'resume/resume-page.html', context)
        
        resume_file = request.FILES['resume_file']
        target_role = request.POST.get('target_role', '')
        
        # Validate file
        if resume_file.size == 0:
            messages.error(request, 'The uploaded file is empty.')
            return render(request, 'resume/resume-page.html', context)
        
        # Check file size (limit to 10MB)
        if resume_file.size > 10 * 1024 * 1024:
            messages.error(request, 'File size must be less than 10MB.')
            return render(request, 'resume/resume-page.html', context)
        
        # Check file type
        allowed_extensions = ['.pdf', '.docx', '.doc', '.txt']
        file_extension = resume_file.name.lower().split('.')[-1]
        if f'.{file_extension}' not in allowed_extensions:
            messages.error(request, 'Please upload a PDF, DOCX, DOC, or TXT file.')
            return render(request, 'resume/resume-page.html', context)
        
        try:
            # Read file content
            file_content = resume_file.read()
            file_name = resume_file.name
            
            # Analyze resume using the agent
            analysis = analyze_resume(
                file_content=file_content,
                file_name=file_name,
                target_role=target_role
            )
            
            # Add analysis to context
            context.update({
                'analysis': analysis,
                'file_name': file_name,
                'target_role': target_role,
                'analysis_completed': True
            })
            
            messages.success(request, 'Resume analyzed successfully!')
            
        except Exception as e:
            messages.error(request, f'Error analyzing resume: {str(e)}')
    
    return render(request, 'resume/resume-page.html', context)


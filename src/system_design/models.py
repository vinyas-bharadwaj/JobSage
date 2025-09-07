from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField
import json

class SystemDesignQuestion(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    company = models.CharField(max_length=100, blank=True)
    difficulty = models.CharField(max_length=20, choices=[
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard')
    ], default='Medium')
    published_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']

class SystemDesignSubmission(models.Model):
    question = models.ForeignKey(SystemDesignQuestion, on_delete=models.CASCADE, related_name='submissions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Store the uploaded design image (nullable for existing records)
    design_image = CloudinaryField(
        'image',
        folder='design_submissions',
        help_text="Uploaded design image",
        null=True,
        blank=True
    )
    
    # Analysis results
    overall_score = models.IntegerField(default=0)
    scalability_score = models.IntegerField(default=0)
    reliability_score = models.IntegerField(default=0)
    
    # Feedback arrays stored as JSON
    strengths = models.JSONField(default=list)
    weaknesses = models.JSONField(default=list)
    missing_components = models.JSONField(default=list)
    recommendations = models.JSONField(default=list)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    analysis_completed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username} - {self.question.title}"
    
    def get_design_image_url(self):
        """Get the URL of the uploaded design image"""
        if self.design_image:
            return self.design_image.url
        return None
    
    def get_design_image_path(self):
        """Get the file path of the uploaded design image"""
        if self.design_image:
            return self.design_image.path
        return None
    
    class Meta:
        ordering = ['-created_at']

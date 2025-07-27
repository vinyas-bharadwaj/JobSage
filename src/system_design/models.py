from django.db import models
from django.contrib.auth.models import User
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
    
    # Store the Excalidraw data
    design_data = models.JSONField(help_text="Excalidraw elements and app state")
    
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
    
    def save_design_data(self, elements, app_state):
        """Helper method to save Excalidraw data"""
        self.design_data = {
            'elements': elements,
            'appState': app_state
        }
    
    def get_design_elements(self):
        """Get design elements from stored data"""
        return self.design_data.get('elements', [])
    
    def get_app_state(self):
        """Get app state from stored data"""
        return self.design_data.get('appState', {})
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['question', 'user']  # One submission per user per question
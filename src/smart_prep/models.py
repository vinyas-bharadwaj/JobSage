import uuid
from django.db import models

class SmartPrepSession(models.Model):
    # User info
    company_name = models.CharField(max_length=200)
    target_role = models.CharField(max_length=200, default="Software Engineer")
    
    # AI generated content
    company_overview = models.TextField()
    key_technologies = models.JSONField(default=list)
    preparation_timeline = models.JSONField(default=dict)
    interview_tips = models.JSONField(default=list)
    practice_resources = models.JSONField(default=list)
    red_flags = models.JSONField(default=list)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=8, unique=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.session_id:
            self.session_id = str(uuid.uuid4())[:8]
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.company_name} - {self.target_role}"
    
    class Meta:
        ordering = ['-created_at']

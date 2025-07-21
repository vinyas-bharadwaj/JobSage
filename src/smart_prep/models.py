from django.db import models
import uuid

class SmartPrepSession(models.Model):
    """Store smart preparation advice for companies"""
    
    # Basic info
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

# Helper function to create session from AI response
def create_session_from_ai(ai_response, user=None, company_name="", target_role=""):
    """Create SmartPrepSession from AI response"""
    return SmartPrepSession.objects.create(
        company_name=company_name,
        target_role=target_role,
        company_overview=ai_response.company_overview,
        key_technologies=ai_response.key_technologies,
        preparation_timeline=ai_response.preparation_timeline,
        interview_tips=ai_response.interview_tips,
        practice_resources=ai_response.practice_resources,
        red_flags=ai_response.red_flags,
    )

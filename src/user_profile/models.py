from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image
from pgvector.django import VectorField
from cloudinary.models import CloudinaryField

class Profile(models.Model):
    # Basic fields
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=300, blank=True)
    location = models.CharField(max_length=50, blank=True)
    avatar = CloudinaryField(
        'image',
        folder='avatars',
        default='avatars/default.webp',
        transformation={'width': 300, 'height': 300, 'crop': 'fill', 'gravity': 'face'}
    )
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    embeddings = VectorField(dimensions=768, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Simple fields for TF-IDF
    interests = models.TextField(
        max_length=300, 
        blank=True, 
        help_text="Your interests (comma-separated): machine learning, web development, data science"
    )
    
    skills = models.TextField(
        max_length=200, 
        blank=True, 
        help_text="Technical skills (comma-separated): Python, React, Docker"
    )
    
    role = models.CharField(
        max_length=50, 
        blank=True, 
        help_text="Your role: Frontend Developer, Data Scientist, etc."
    )
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    @property
    def interests_list(self):
        """Returns interests as a list for TF-IDF"""
        if self.interests:
            return [i.strip().lower() for i in self.interests.split(',') if i.strip()]
        return []
    
    @property
    def skills_list(self):
        """Returns skills as a list for TF-IDF"""
        if self.skills:
            return [s.strip().lower() for s in self.skills.split(',') if s.strip()]
        return []
    
    def get_text_for_matching(self):
        """Simple method to get all text for TF-IDF matching"""
        text_parts = []
        
        if self.bio:
            text_parts.append(self.bio.lower())
        if self.role:
            text_parts.append(self.role.lower())
        
        text_parts.extend(self.interests_list)
        text_parts.extend(self.skills_list)
        
        return ' '.join(text_parts)
    
    def save(self, *args, **kwargs):
        # Note: Image resizing is now handled by Cloudinary transformations
        # The avatar field is configured with automatic cropping and resizing
        super().save(*args, **kwargs)

# Auto-create profile when user is created
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

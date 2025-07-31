from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image
import os

class Profile(models.Model):
    # Basic fields
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=300, blank=True)
    location = models.CharField(max_length=50, blank=True)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.webp')
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
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
        super().save(*args, **kwargs)
        
        # Resize avatar if it exists and is not the default
        if self.avatar and hasattr(self.avatar, 'path') and 'default.webp' not in self.avatar.name:
            try:
                img = Image.open(self.avatar.path)
                
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                
                # Resize to 100x100
                max_size = (100, 100)
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Make it square
                width, height = img.size
                if width != height:
                    min_dimension = min(width, height)
                    left = (width - min_dimension) // 2
                    top = (height - min_dimension) // 2
                    right = left + min_dimension
                    bottom = top + min_dimension
                    img = img.crop((left, top, right, bottom))
                
                img.save(self.avatar.path, 'JPEG', quality=85, optimize=True)
                
            except Exception as e:
                print(f"Image resize failed: {e}")
                pass

# Auto-create profile when user is created
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

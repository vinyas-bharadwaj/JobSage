from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse

class Blog(models.Model):
    # Basic fields
    title = models.CharField(max_length=200)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)
    
    # Fields for TF-IDF matching with user profiles
    tags = models.CharField(
        max_length=200, 
        blank=True,
        help_text="Tags (comma-separated): python, web development, machine learning"
    )
    
    category = models.CharField(
        max_length=50,
        blank=True,
        help_text="Category: Tutorial, News, Career Advice, etc."
    )
    
    target_role = models.CharField(
        max_length=50,
        blank=True,
        help_text="Target role: Frontend Developer, Data Scientist, etc."
    )
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('blog_detail', kwargs={'pk': self.pk})
    
    @property
    def tags_list(self):
        """Returns tags as a list for TF-IDF"""
        if self.tags:
            return [t.strip().lower() for t in self.tags.split(',') if t.strip()]
        return []
    
    def get_text_for_matching(self):
        """Get all text for TF-IDF matching with user profiles"""
        text_parts = []
        
        # Include title and content (first 500 chars to avoid too much noise)
        text_parts.append(self.title.lower())
        text_parts.append(self.content[:500].lower())
        
        # Include category and target role
        if self.category:
            text_parts.append(self.category.lower())
        if self.target_role:
            text_parts.append(self.target_role.lower())
        
        # Include tags
        text_parts.extend(self.tags_list)
        
        return ' '.join(text_parts)

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from pgvector.django import VectorField

class Blog(models.Model):
    # Basic fields
    title = models.CharField(max_length=200)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    embeddings = VectorField(dimensions=768, null=True, blank=True)
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
    def info(self):
        """Returns combination of tags, content, category, target_role as an array"""
        info_array = []
        
        # Add tags
        if self.tags:
            info_array.extend([t.strip().lower() for t in self.tags.split(',') if t.strip()])
        
        # Add content
        if self.content:
            info_array.append(self.content.strip())
        
        # Add category
        if self.category:
            info_array.append(self.category.strip().lower())
        
        # Add target_role
        if self.target_role:
            info_array.append(self.target_role.strip().lower())
        
        return info_array
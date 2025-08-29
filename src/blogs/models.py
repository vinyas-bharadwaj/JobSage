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
        max_length=100,
        blank=True,
        help_text="Category of the blog post"
    )
    
    target_role = models.CharField(
        max_length=200,  # Increased from 50 to 200
        blank=True,
        help_text="Target roles (comma-separated): Software Engineer, Data Scientist"
    )

    @property
    def info(self):
        """Return a list of strings representing the blog information for TF-IDF matching."""
        info_list = []
        if self.title:
            info_list.append(self.title)
        if self.content:
            info_list.append(self.content)
        if self.tags:
            info_list.append(self.tags)
        if self.category:
            info_list.append(self.category)
        if self.target_role:
            info_list.append(self.target_role)
        return info_list

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
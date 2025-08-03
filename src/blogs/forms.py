from django import forms
from .models import Blog

class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['title', 'content', 'tags', 'category', 'target_role', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter blog title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Write your blog content here...'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'python, django, web development'}),
            'category': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tutorial, News, Career Advice'}),
            'target_role': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Frontend Developer, Data Scientist'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
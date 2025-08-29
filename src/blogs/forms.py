from django import forms
from .models import Blog

class BlogForm(forms.ModelForm):
    CATEGORY_CHOICES = [
        ('', 'Select a category'),
        ('web-development', 'Web Development'),
        ('mobile-development', 'Mobile Development'),
        ('data-science', 'Data Science'),
        ('machine-learning', 'Machine Learning'),
        ('artificial-intelligence', 'Artificial Intelligence'),
        ('backend-development', 'Backend Development'),
        ('frontend-development', 'Frontend Development'),
        ('devops', 'DevOps'),
        ('cloud-computing', 'Cloud Computing'),
        ('cybersecurity', 'Cybersecurity'),
        ('software-engineering', 'Software Engineering'),
        ('algorithms', 'Algorithms & Data Structures'),
        ('system-design', 'System Design'),
        ('career-advice', 'Career Advice'),
        ('interview-prep', 'Interview Preparation'),
        ('tutorials', 'Tutorials'),
        ('best-practices', 'Best Practices'),
        ('tools-and-technologies', 'Tools & Technologies'),
        ('open-source', 'Open Source'),
    ]

    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        required=False
    )

    class Meta:
        model = Blog
        fields = ['title', 'content', 'tags', 'category', 'target_role', 'is_published']
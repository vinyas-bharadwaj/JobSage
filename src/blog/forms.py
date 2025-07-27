from django import forms
from .models import Blog, Category

class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['title', 'content', 'excerpt', 'featured_image', 'category', 'status', 'reading_time', 'is_featured']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Enter blog title...',
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control rich-text-editor',
                'rows': 20,
                'placeholder': 'Write your blog content here...',
            }),
            'excerpt': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Brief summary of your blog post...',
                'maxlength': 300,
            }),
            'featured_image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
            }),
            'status': forms.Select(attrs={
                'class': 'form-select',
            }),
            'reading_time': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 60,
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()
        self.fields['category'].empty_label = "Select a category"
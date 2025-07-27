from django import forms
from .models import SystemDesignQuestion, SystemDesignSubmission
import json

class SystemDesignQuestionForm(forms.ModelForm):
    class Meta:
        model = SystemDesignQuestion
        fields = ['title', 'description', 'company', 'difficulty']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Design a URL Shortener like bit.ly',
                'id': 'title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the system requirements, constraints, scale expectations, and any specific features...',
                'id': 'description'
            }),
            'company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Google, Amazon, Meta, Netflix',
                'id': 'company',
                'required': False
            }),
            'difficulty': forms.Select(attrs={
                'class': 'form-select',
                'id': 'difficulty'
            }, choices=[
                ('Easy', 'Easy'),
                ('Medium', 'Medium'),
                ('Hard', 'Hard')
            ])
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['company'].required = False
        self.fields['difficulty'].initial = 'Medium'

class SystemDesignSubmissionForm(forms.ModelForm):
    # Hidden field to store Excalidraw data
    excalidraw_elements = forms.CharField(widget=forms.HiddenInput(), required=True)
    excalidraw_app_state = forms.CharField(widget=forms.HiddenInput(), required=False)
    
    class Meta:
        model = SystemDesignSubmission
        fields = ['excalidraw_elements', 'excalidraw_app_state']
    
    def clean_excalidraw_elements(self):
        elements_data = self.cleaned_data['excalidraw_elements']
        try:
            # Validate that it's proper JSON
            elements = json.loads(elements_data)
            if not isinstance(elements, list):
                raise forms.ValidationError("Elements must be a list")
            if len(elements) == 0:
                raise forms.ValidationError("Please draw your system design before submitting")
            return elements_data
        except json.JSONDecodeError:
            raise forms.ValidationError("Invalid design data")
    
    def clean_excalidraw_app_state(self):
        app_state_data = self.cleaned_data.get('excalidraw_app_state', '{}')
        try:
            json.loads(app_state_data)
            return app_state_data
        except json.JSONDecodeError:
            return '{}'
from django import forms
from .models import SystemDesignQuestion, SystemDesignSubmission
import json

class SystemDesignQuestionForm(forms.ModelForm):
    class Meta:
        model = SystemDesignQuestion
        fields = ['title', 'description', 'difficulty']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500',
                'placeholder': 'Enter question title...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500',
                'rows': 4,
                'placeholder': 'Describe the system design problem...'
            }),
            'difficulty': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500'
            })
        }

class SystemDesignSubmissionForm(forms.Form):
    excalidraw_elements = forms.CharField(widget=forms.HiddenInput())
    excalidraw_app_state = forms.CharField(widget=forms.HiddenInput(), required=False)
    
    def clean_excalidraw_elements(self):
        elements = self.cleaned_data['excalidraw_elements']
        try:
            parsed_elements = json.loads(elements)
            if not isinstance(parsed_elements, list):
                raise forms.ValidationError("Invalid elements format")
            return elements
        except (json.JSONDecodeError, TypeError):
            raise forms.ValidationError("Invalid JSON format for elements")
    
    def clean_excalidraw_app_state(self):
        app_state = self.cleaned_data.get('excalidraw_app_state', '{}')
        if not app_state:
            return '{}'
        try:
            json.loads(app_state)
            return app_state
        except (json.JSONDecodeError, TypeError):
            raise forms.ValidationError("Invalid JSON format for app state")
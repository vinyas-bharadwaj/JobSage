# smart_prep/forms.py
from django import forms

class SmartPrepForm(forms.Form):
    company_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter company name (e.g., Google, Microsoft)',
            'required': True,
            'id': 'companyName'
        }),
        label='Company Name'
    )
    
    target_role = forms.CharField(
        max_length=255,
        initial='Software Engineer',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Target role (e.g., Software Engineer, Product Manager)',
            'id': 'targetRole'
        }),
        label='Target Role'
    )
    
    user_experience = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Tell us about your experience, skills, and background (optional)',
            'rows': 3,
            'id': 'userExperience'
        }),
        label='Your Experience (Optional)'
    )

    def clean_company_name(self):
        company_name = self.cleaned_data.get('company_name', '').strip()
        if not company_name:
            raise forms.ValidationError("Company name is required.")
        return company_name.title()  # Capitalize properly

    def clean_target_role(self):
        target_role = self.cleaned_data.get('target_role', '').strip()
        if not target_role:
            return 'Software Engineer'  # Default value
        return target_role.title()
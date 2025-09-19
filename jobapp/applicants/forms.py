from django import forms
from django.contrib.auth.models import User
from .models import ApplicantProfile, Education, WorkExperience

class ApplicantProfileForm(forms.ModelForm):
    """Form for creating and editing applicant profiles"""

    class Meta:
        model = ApplicantProfile
        fields = [
            'headline', 'phone', 'city', 'state', 'country', 'postal_code',
            'latitude', 'longitude', 'willing_to_relocate', 'remote_work_preference',
            'summary', 'skills', 'linkedin_url', 'github_url', 'portfolio_url', 'other_url',
            'is_public', 'is_seeking_jobs'
        ]
        widgets = {
            'headline': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Software Developer with 5 years experience'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1 (555) 123-4567'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., San Francisco'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., California'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., United States'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 94105'
            }),
            'latitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.000001',
                'placeholder': '37.7749'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.000001',
                'placeholder': '-122.4194'
            }),
            'summary': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell recruiters about your professional background and career goals...'
            }),
            'skills': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'List your key skills separated by commas (e.g., Python, Django, React, SQL)'
            }),
            'linkedin_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://linkedin.com/in/yourprofile'
            }),
            'github_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://github.com/yourusername'
            }),
            'portfolio_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://yourportfolio.com'
            }),
            'other_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Any other relevant professional URL'
            }),
            'willing_to_relocate': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'remote_work_preference': forms.Select(attrs={'class': 'form-control'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_seeking_jobs': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'headline': 'Professional Headline',
            'phone': 'Phone Number',
            'city': 'City',
            'state': 'State/Province',
            'country': 'Country',
            'postal_code': 'Postal/ZIP Code',
            'latitude': 'Latitude (optional)',
            'longitude': 'Longitude (optional)',
            'willing_to_relocate': 'Willing to relocate for work',
            'remote_work_preference': 'Remote work preference',
            'summary': 'Professional Summary',
            'skills': 'Skills',
            'linkedin_url': 'LinkedIn Profile',
            'github_url': 'GitHub Profile',
            'portfolio_url': 'Portfolio Website',
            'other_url': 'Other Professional URL',
            'is_public': 'Make profile visible to recruiters',
            'is_seeking_jobs': 'Currently seeking job opportunities',
        }

class EducationForm(forms.ModelForm):
    """Form for adding/editing education records"""

    class Meta:
        model = Education
        fields = [
            'institution', 'degree', 'field_of_study', 'start_date', 'end_date',
            'is_current', 'gpa', 'description', 'order'
        ]
        widgets = {
            'institution': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Stanford University'
            }),
            'degree': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Bachelor of Science'
            }),
            'field_of_study': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Computer Science'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'gpa': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '4.0',
                'placeholder': '3.75'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional details about your education...'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0'
            }),
            'is_current': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'institution': 'Institution Name',
            'degree': 'Degree Type',
            'field_of_study': 'Field of Study',
            'start_date': 'Start Date',
            'end_date': 'End Date',
            'is_current': 'Currently studying here',
            'gpa': 'GPA (optional)',
            'description': 'Additional Details',
            'order': 'Display Order (higher numbers first)',
        }

class WorkExperienceForm(forms.ModelForm):
    """Form for adding/editing work experience records"""

    class Meta:
        model = WorkExperience
        fields = [
            'company', 'position', 'start_date', 'end_date', 'is_current',
            'location', 'description', 'order'
        ]
        widgets = {
            'company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Google Inc.'
            }),
            'position': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Senior Software Engineer'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Mountain View, CA'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe your responsibilities and achievements...'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0'
            }),
            'is_current': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'company': 'Company Name',
            'position': 'Job Title',
            'start_date': 'Start Date',
            'end_date': 'End Date',
            'is_current': 'Currently working here',
            'location': 'Work Location',
            'description': 'Job Description',
            'order': 'Display Order (higher numbers first)',
        }

class EducationFormSet(forms.BaseInlineFormSet):
    """Formset for managing multiple education records"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = True

class WorkExperienceFormSet(forms.BaseInlineFormSet):
    """Formset for managing multiple work experience records"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = True

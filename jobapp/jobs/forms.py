from django import forms
from .models import Job, JobApplication

class JobForm(forms.ModelForm):
    """Form for creating and editing job postings"""
    
    class Meta:
        model = Job
        fields = [
            'title', 'company', 'description', 'requirements',
            'job_type', 'remote_type', 'experience_level',
            'salary_min', 'salary_max', 'salary_currency', 'salary_period',
            'city', 'state', 'country', 'postal_code',
            'required_skills', 'preferred_skills',
            'visa_sponsorship', 'benefits', 'application_deadline'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Senior Software Engineer'}),
            'company': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'job_type': forms.Select(attrs={'class': 'form-control'}),
            'remote_type': forms.Select(attrs={'class': 'form-control'}),
            'experience_level': forms.Select(attrs={'class': 'form-control'}),
            'salary_min': forms.NumberInput(attrs={'class': 'form-control', 'step': '1000'}),
            'salary_max': forms.NumberInput(attrs={'class': 'form-control', 'step': '1000'}),
            'salary_currency': forms.TextInput(attrs={'class': 'form-control', 'value': 'USD'}),
            'salary_period': forms.Select(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'value': 'United States'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'required_skills': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Python, Django, React, SQL'}),
            'preferred_skills': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'benefits': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'application_deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'visa_sponsorship': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class JobSearchForm(forms.Form):
    """Form for job search with filters"""
    
    keywords = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Job title, company, or keywords...'
        })
    )
    
    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City, state, or country...'
        })
    )
    
    job_type = forms.MultipleChoiceField(
        choices=Job.JOB_TYPE_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )
    
    remote_type = forms.MultipleChoiceField(
        choices=Job.REMOTE_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )
    
    experience_level = forms.MultipleChoiceField(
        choices=Job.EXPERIENCE_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )
    
    salary_min = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Minimum salary'
        })
    )
    
    visa_sponsorship = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    skills = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Required skills (comma separated)...'
        })
    )

class JobApplicationForm(forms.ModelForm):
    """Form for applying to jobs"""
    
    class Meta:
        model = JobApplication
        fields = ['cover_letter']
        widgets = {
            'cover_letter': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Write a personalized note or cover letter (optional)...'
            })
        }
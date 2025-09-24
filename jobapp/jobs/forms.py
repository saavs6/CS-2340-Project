from django import forms
from .models import Job, JobApplication

class JobForm(forms.ModelForm):
    """Form for creating and editing job postings"""
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title and len(title.strip()) < 3:
            raise forms.ValidationError("Job title must be at least 3 characters long.")
        return title.strip() if title else title

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if description and len(description.strip()) < 20:
            raise forms.ValidationError("Job description must be at least 20 characters long.")
        return description.strip() if description else description

    def clean_requirements(self):
        requirements = self.cleaned_data.get('requirements')
        if requirements and len(requirements.strip()) < 10:
            raise forms.ValidationError("Job requirements must be at least 10 characters long.")
        return requirements.strip() if requirements else requirements

    def clean(self):
        cleaned_data = super().clean()
        salary_min = cleaned_data.get('salary_min')
        salary_max = cleaned_data.get('salary_max')
        
        if salary_min and salary_max:
            if salary_min >= salary_max:
                raise forms.ValidationError("Maximum salary must be greater than minimum salary.")
        
        return cleaned_data
    
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
            'title': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., Senior Software Engineer',
                'required': True,
                'maxlength': 200
            }),
            'company': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Company Name',
                'required': True,
                'maxlength': 200
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 6,
                'required': True,
                'placeholder': 'Describe the job role, responsibilities, and what makes this position exciting...'
            }),
            'requirements': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'required': True,
                'placeholder': 'List the qualifications, experience, and requirements for this position...'
            }),
            'job_type': forms.Select(attrs={'class': 'form-control'}),
            'remote_type': forms.Select(attrs={'class': 'form-control'}),
            'experience_level': forms.Select(attrs={'class': 'form-control'}),
            'salary_min': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '1000',
                'min': '0',
                'placeholder': '50000'
            }),
            'salary_max': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '1000',
                'min': '0',
                'placeholder': '100000'
            }),
            'salary_currency': forms.TextInput(attrs={
                'class': 'form-control', 
                'value': 'USD',
                'maxlength': 3
            }),
            'salary_period': forms.Select(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True,
                'placeholder': 'e.g., San Francisco',
                'maxlength': 100
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True,
                'placeholder': 'e.g., California',
                'maxlength': 100
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control', 
                'value': 'United States',
                'maxlength': 100
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 94105',
                'maxlength': 20
            }),
            'required_skills': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 2, 
                'placeholder': 'Python, Django, React, SQL'
            }),
            'preferred_skills': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 2,
                'placeholder': 'Docker, AWS, Machine Learning'
            }),
            'benefits': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'Health insurance, 401k, flexible hours, remote work options...'
            }),
            'application_deadline': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date'
            }),
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
from django import forms
from .models import RecruiterProfile

class RecruiterProfileForm(forms.ModelForm):
    """Form for recruiter profile management"""
    
    class Meta:
        model = RecruiterProfile
        fields = [
            'company_name', 'company_size', 'industry', 'phone', 'website',
            'city', 'state', 'country', 'company_description'
        ]
        widgets = {
            'company_description': forms.Textarea(attrs={'rows': 4}),
        }

class CandidateSearchForm(forms.Form):
    """Form for searching candidates by various criteria"""
    
    # Keywords search
    keywords = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search by name, headline, or summary...',
            'class': 'form-control'
        }),
        help_text="Search by candidate name, headline, or professional summary"
    )
    
    # Skills search
    skills = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Python, Django, React, SQL...',
            'class': 'form-control'
        }),
        help_text="Enter skills separated by commas"
    )
    
    # Location search
    location = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'City, State, or Country',
            'class': 'form-control'
        }),
        help_text="Search by location"
    )
    
    # Remote work preference
    remote_preference = forms.ChoiceField(
        choices=[
            ('', 'Any'),
            ('remote_only', 'Remote Only'),
            ('hybrid', 'Hybrid'),
            ('onsite_only', 'Onsite Only'),
            ('flexible', 'Flexible'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Willing to relocate
    willing_to_relocate = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    # Currently seeking jobs
    is_seeking_jobs = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    # Experience level (based on work experience)
    experience_years = forms.ChoiceField(
        choices=[
            ('', 'Any'),
            ('0-2', '0-2 years'),
            ('3-5', '3-5 years'),
            ('6-10', '6-10 years'),
            ('10+', '10+ years'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Education level
    education_level = forms.ChoiceField(
        choices=[
            ('', 'Any'),
            ('high_school', 'High School'),
            ('associate', 'Associate Degree'),
            ('bachelor', "Bachelor's Degree"),
            ('master', "Master's Degree"),
            ('phd', 'PhD'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def clean_skills(self):
        """Clean and validate skills input"""
        skills = self.cleaned_data.get('skills', '')
        if skills:
            # Split by comma and clean up
            skill_list = [skill.strip() for skill in skills.split(',') if skill.strip()]
            return ', '.join(skill_list)
        return skills

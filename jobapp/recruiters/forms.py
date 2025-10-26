from django import forms
from django.contrib.auth.models import User
from .models import RecruiterProfile
from .models import SavedSearch

class RecruiterProfileForm(forms.ModelForm):
    """Form for recruiter profile management"""
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'you@company.com'}),
        label='Contact Email',
        help_text='Used to contact candidates via email.'
    )

    class Meta:
        model = RecruiterProfile
        fields = [
            'company_name', 'company_size', 'industry', 'phone', 'website',
            'city', 'state', 'country', 'company_description'
        ]
        widgets = {
            'company_description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-fill from bound instance's related user
        if getattr(self.instance, 'user', None):
            self.fields['email'].initial = self.instance.user.email

        # Ensure consistent Bootstrap styling across all fields (match email)
        for name, field in self.fields.items():
            # Skip email since it's already configured explicitly above
            if name == 'email':
                continue

            widget = field.widget
            # For checkbox-like widgets use form-check-input, otherwise form-control
            from django.forms import CheckboxInput
            if isinstance(widget, CheckboxInput):
                existing = widget.attrs.get('class', '')
                if 'form-check-input' not in existing:
                    widget.attrs['class'] = (existing + ' form-check-input').strip()
            else:
                existing = widget.attrs.get('class', '')
                if 'form-control' not in existing:
                    widget.attrs['class'] = (existing + ' form-control').strip()
    def save(self, commit=True):
        profile = super().save(commit)
        email = self.cleaned_data.get('email', '').strip()
        if getattr(profile, 'user', None) is not None:
            profile.user.email = email
            if commit:
                profile.user.save(update_fields=['email'])
        return profile

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


class SavedSearchForm(forms.ModelForm):
    class Meta:
        model = SavedSearch
        fields = [
            'name', 'keywords', 'skills', 'location', 'remote_preference',
            'experience_years', 'education_level', 'willing_to_relocate',
            'is_seeking_jobs', 'notification_frequency', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'keywords': forms.TextInput(attrs={'class': 'form-control'}),
            'skills': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'remote_preference': forms.Select(attrs={'class': 'form-control'}),
            'experience_years': forms.Select(attrs={'class': 'form-control'}),
            'education_level': forms.Select(attrs={'class': 'form-control'}),
            'willing_to_relocate': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_seeking_jobs': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notification_frequency': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


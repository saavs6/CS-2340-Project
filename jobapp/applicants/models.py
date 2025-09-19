from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin

class ApplicantProfile(models.Model):
    """Extended profile for job applicants with professional information"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='applicant_profile')

    # Basic professional info
    headline = models.CharField(
        max_length=200,
        blank=True,
        help_text="A brief professional headline (e.g., 'Software Developer with 5 years experience')"
    )

    # Contact and location
    phone = models.CharField(max_length=20, blank=True)

    # Location fields for future map/distance functionality
    city = models.CharField(max_length=100, blank=True, help_text="City")
    state = models.CharField(max_length=100, blank=True, help_text="State or Province")
    country = models.CharField(max_length=100, blank=True, help_text="Country")
    postal_code = models.CharField(max_length=20, blank=True, help_text="Postal/ZIP Code")

    # Coordinates for map functionality (optional, can be auto-populated)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        help_text="Latitude coordinate (auto-populated if possible)"
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        help_text="Longitude coordinate (auto-populated if possible)"
    )

    # Display location (for backward compatibility and display)
    location = models.CharField(max_length=200, blank=True, help_text="Full location display (auto-generated)")

    # Location preferences
    willing_to_relocate = models.BooleanField(default=False, help_text="Willing to relocate for work")
    remote_work_preference = models.CharField(
        max_length=20,
        choices=[
            ('remote_only', 'Remote Only'),
            ('hybrid', 'Hybrid'),
            ('onsite_only', 'Onsite Only'),
            ('flexible', 'Flexible'),
        ],
        default='flexible',
        help_text="Remote work preference"
    )

    # Professional summary
    summary = models.TextField(
        blank=True,
        help_text="A brief summary of your professional background and career goals"
    )

    # Skills (stored as comma-separated values for simplicity)
    skills = models.TextField(
        blank=True,
        help_text="List your key skills separated by commas (e.g., 'Python, Django, React, SQL')"
    )

    # Social and professional links
    linkedin_url = models.URLField(blank=True, help_text="Your LinkedIn profile URL")
    github_url = models.URLField(blank=True, help_text="Your GitHub profile URL")
    portfolio_url = models.URLField(blank=True, help_text="Your portfolio or personal website URL")
    other_url = models.URLField(blank=True, help_text="Any other relevant professional URL")

    # Profile visibility and status
    is_public = models.BooleanField(default=True, help_text="Make profile visible to recruiters")
    is_seeking_jobs = models.BooleanField(default=True, help_text="Currently looking for job opportunities")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.headline or 'No headline'}"

    def get_skills_list(self):
        """Return skills as a list"""
        if self.skills:
            return [skill.strip() for skill in self.skills.split(',') if skill.strip()]
        return []

    def set_skills_list(self, skills_list):
        """Set skills from a list"""
        self.skills = ', '.join(skills_list)

    def get_full_location(self):
        """Get formatted full location string"""
        location_parts = []
        if self.city:
            location_parts.append(self.city)
        if self.state:
            location_parts.append(self.state)
        if self.country:
            location_parts.append(self.country)
        return ', '.join(location_parts) if location_parts else ''

    def get_short_location(self):
        """Get short location string (city, state)"""
        location_parts = []
        if self.city:
            location_parts.append(self.city)
        if self.state:
            location_parts.append(self.state)
        return ', '.join(location_parts) if location_parts else ''

    def has_coordinates(self):
        """Check if coordinates are available for mapping"""
        return self.latitude is not None and self.longitude is not None

    def get_coordinates(self):
        """Get coordinates as tuple if available"""
        if self.has_coordinates():
            return (float(self.latitude), float(self.longitude))
        return None

    def save(self, *args, **kwargs):
        """Override save to auto-generate location display"""
        # Auto-generate location display
        self.location = self.get_full_location()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Applicant Profile"
        verbose_name_plural = "Applicant Profiles"

class Education(models.Model):
    """Educational background for applicants"""

    applicant = models.ForeignKey(ApplicantProfile, on_delete=models.CASCADE, related_name='education')

    institution = models.CharField(max_length=200, help_text="Name of school or university")
    degree = models.CharField(max_length=100, help_text="Degree type (e.g., Bachelor's, Master's)")
    field_of_study = models.CharField(max_length=100, help_text="Field of study (e.g., Computer Science)")

    # Dates
    start_date = models.DateField(help_text="Start date of education")
    end_date = models.DateField(null=True, blank=True, help_text="End date (leave blank if currently studying)")
    is_current = models.BooleanField(default=False, help_text="Currently studying here")

    # Additional info
    gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True, help_text="GPA (optional)")
    description = models.TextField(blank=True, help_text="Additional details about your education")

    # Order for display
    order = models.PositiveIntegerField(default=0, help_text="Order for display (higher numbers first)")

    def __str__(self):
        return f"{self.degree} in {self.field_of_study} - {self.institution}"

    class Meta:
        ordering = ['-order', '-end_date', '-start_date']
        verbose_name = "Education"
        verbose_name_plural = "Education Records"

class WorkExperience(models.Model):
    """Work experience for applicants"""

    applicant = models.ForeignKey(ApplicantProfile, on_delete=models.CASCADE, related_name='work_experience')

    company = models.CharField(max_length=200, help_text="Company name")
    position = models.CharField(max_length=200, help_text="Job title or position")

    # Dates
    start_date = models.DateField(help_text="Start date of employment")
    end_date = models.DateField(null=True, blank=True, help_text="End date (leave blank if currently working)")
    is_current = models.BooleanField(default=False, help_text="Currently working here")

    # Job details
    location = models.CharField(max_length=100, blank=True, help_text="Work location")
    description = models.TextField(help_text="Describe your responsibilities and achievements")

    # Order for display
    order = models.PositiveIntegerField(default=0, help_text="Order for display (higher numbers first)")

    def __str__(self):
        return f"{self.position} at {self.company}"

    class Meta:
        ordering = ['-order', '-end_date', '-start_date']
        verbose_name = "Work Experience"
        verbose_name_plural = "Work Experience Records"

# Admin registration
@admin.register(ApplicantProfile)
class ApplicantProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'headline', 'location', 'is_public', 'is_seeking_jobs', 'created_at']
    list_filter = ['is_public', 'is_seeking_jobs', 'created_at']
    search_fields = ['user__username', 'user__email', 'headline', 'location']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ['applicant', 'institution', 'degree', 'field_of_study', 'start_date', 'end_date']
    list_filter = ['degree', 'is_current']
    search_fields = ['institution', 'field_of_study', 'applicant__user__username']

@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    list_display = ['applicant', 'company', 'position', 'start_date', 'end_date', 'is_current']
    list_filter = ['is_current']
    search_fields = ['company', 'position', 'applicant__user__username']
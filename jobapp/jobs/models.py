from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal

class Job(models.Model):
    """Main job posting model"""
    
    # Job Type Choices
    JOB_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('temporary', 'Temporary'),
    ]
    
    REMOTE_CHOICES = [
        ('remote', 'Remote'),
        ('hybrid', 'Hybrid'),
        ('onsite', 'On-site'),
    ]
    
    EXPERIENCE_CHOICES = [
        ('entry', 'Entry Level (0-2 years)'),
        ('mid', 'Mid Level (3-5 years)'),
        ('senior', 'Senior Level (6+ years)'),
        ('executive', 'Executive Level'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    description = models.TextField()
    requirements = models.TextField(help_text="Job requirements and qualifications")
    
    # Recruiter who posted this job
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_jobs')
    
    # Job Details
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='full_time')
    remote_type = models.CharField(max_length=20, choices=REMOTE_CHOICES, default='onsite')
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default='mid')
    
    # Salary Information
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_currency = models.CharField(max_length=3, default='USD')
    salary_period = models.CharField(max_length=20, choices=[
        ('hourly', 'Per Hour'),
        ('monthly', 'Per Month'),
        ('yearly', 'Per Year'),
    ], default='yearly')
    
    # Location Information
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='United States')
    postal_code = models.CharField(max_length=20, blank=True)
    
    
    # Skills (comma-separated for simplicity)
    required_skills = models.TextField(blank=True, help_text="Required skills, separated by commas")
    preferred_skills = models.TextField(blank=True, help_text="Preferred skills, separated by commas")
    
    # Additional Information
    visa_sponsorship = models.BooleanField(default=False, help_text="Visa sponsorship available")
    benefits = models.TextField(blank=True, help_text="Benefits and perks")
    
    # Status and Timestamps
    is_active = models.BooleanField(default=True)
    application_deadline = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Job Posting'
        verbose_name_plural = 'Job Postings'
    
    def __str__(self):
        return f"{self.title} at {self.company}"
    
    def get_absolute_url(self):
        return reverse('jobs:detail', kwargs={'pk': self.pk})
    
    def get_location_display(self):
        """Get formatted location string"""
        return f"{self.city}, {self.state}, {self.country}"
    
    def get_salary_display(self):
        """Get formatted salary range"""
        if self.salary_min and self.salary_max:
            return f"${self.salary_min:,.0f} - ${self.salary_max:,.0f} {self.get_salary_period_display()}"
        elif self.salary_min:
            return f"${self.salary_min:,.0f}+ {self.get_salary_period_display()}"
        return "Salary not specified"
    
    def get_required_skills_list(self):
        """Return required skills as a list"""
        if self.required_skills:
            return [skill.strip() for skill in self.required_skills.split(',') if skill.strip()]
        return []
    
    def get_preferred_skills_list(self):
        """Return preferred skills as a list"""
        if self.preferred_skills:
            return [skill.strip() for skill in self.preferred_skills.split(',') if skill.strip()]
        return []

class JobApplication(models.Model):
    """Track job applications from applicants"""
    
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('review', 'Under Review'),
        ('interview', 'Interview'),
        ('offer', 'Offer Extended'),
        ('accepted', 'Offer Accepted'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_applications')
    
    # Application Details
    cover_letter = models.TextField(blank=True, help_text="Optional cover letter or note")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    
    # Timestamps
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['job', 'applicant']  # Prevent duplicate applications
        ordering = ['-applied_at']
    
    def __str__(self):
        return f"{self.applicant.username} -> {self.job.title}"
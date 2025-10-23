from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from django.utils import timezone
from django.contrib.auth.models import User
import json

class RecruiterProfile(models.Model):
    """Extended profile for recruiters with company information"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='recruiter_profile')
    
    # Company Information
    company_name = models.CharField(max_length=200, help_text="Company or organization name")
    company_size = models.CharField(
        max_length=20,
        choices=[
            ('startup', 'Startup (1-10 employees)'),
            ('small', 'Small (11-50 employees)'),
            ('medium', 'Medium (51-200 employees)'),
            ('large', 'Large (201-1000 employees)'),
            ('enterprise', 'Enterprise (1000+ employees)'),
        ],
        default='medium',
        help_text="Company size"
    )
    industry = models.CharField(max_length=100, blank=True, help_text="Industry or sector")
    
    # Contact Information
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True, help_text="Company website")
    
    # Location
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # Company Description
    company_description = models.TextField(blank=True, help_text="Brief description of your company")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.company_name}"
    
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
    
    class Meta:
        verbose_name = "Recruiter Profile"
        verbose_name_plural = "Recruiter Profiles"

# Admin registration
@admin.register(RecruiterProfile)
class RecruiterProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'company_name', 'company_size', 'industry', 'created_at']
    list_filter = ['company_size', 'industry', 'created_at']
    search_fields = ['user__username', 'user__email', 'company_name', 'industry']
    readonly_fields = ['created_at', 'updated_at']


class SavedSearch(models.Model):
    """Saved candidate search for recruiters"""

    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('never', 'Never'),
    ]

    recruiter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_searches')
    name = models.CharField(max_length=200, help_text='Name for this saved search')
    keywords = models.CharField(max_length=200, blank=True, help_text='Search keywords')
    skills = models.CharField(max_length=500, blank=True, help_text='Required skills')
    location = models.CharField(max_length=200, blank=True, help_text='Location preference')
    remote_preference = models.CharField(max_length=20, blank=True, choices=[('', 'Any'), ('remote_only', 'Remote Only'), ('hybrid', 'Hybrid'), ('onsite_only', 'Onsite Only'), ('flexible', 'Flexible')], help_text='Remote work preference')
    experience_years = models.CharField(max_length=10, blank=True, choices=[('', 'Any'), ('0-2', '0-2 years'), ('3-5', '3-5 years'), ('6-10', '6-10 years'), ('10+', '10+ years')], help_text='Experience level')
    education_level = models.CharField(max_length=20, blank=True, choices=[('', 'Any'), ('high_school', 'High School'), ('associate', 'Associate Degree'), ('bachelor', "Bachelor's Degree"), ('master', "Master's Degree"), ('phd', 'PhD')], help_text='Education level')
    willing_to_relocate = models.BooleanField(default=False, help_text='Must be willing to relocate')
    is_seeking_jobs = models.BooleanField(default=True, help_text='Must be actively seeking jobs')
    notification_frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='weekly', help_text='How often to receive notifications about new matches')
    is_active = models.BooleanField(default=True, help_text='Whether this search is active')
    last_notified = models.DateTimeField(null=True, blank=True, help_text='Last time notifications were sent')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Saved Search'
        verbose_name_plural = 'Saved Searches'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.recruiter.username})"


@admin.register(SavedSearch)
class SavedSearchAdmin(admin.ModelAdmin):
    list_display = ['name', 'recruiter', 'notification_frequency', 'is_active', 'last_notified', 'created_at']
    list_filter = ['notification_frequency', 'is_active', 'created_at']
    search_fields = ['name', 'keywords', 'skills', 'recruiter__username']

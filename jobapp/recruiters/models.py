from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin

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

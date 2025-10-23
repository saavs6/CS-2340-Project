from django.contrib import admin
from .models import Job
from .models import JobRecommendation

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'posted_by', 'city', 'state', 'job_type', 'is_active', 'created_at']
    list_filter = ['job_type', 'remote_type', 'is_active', 'visa_sponsorship', 'created_at']
    search_fields = ['title', 'company', 'city', 'required_skills']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(JobRecommendation)
class JobRecommendationAdmin(admin.ModelAdmin):
    list_display = ['job', 'applicant', 'match_score', 'is_viewed', 'is_applied', 'is_dismissed', 'created_at']
    search_fields = ['job__title', 'applicant__username', 'matched_skills']
    readonly_fields = ['created_at', 'updated_at']
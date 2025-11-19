from django.contrib import admin
from .models import Job
from django.utils.html import format_html
from .models import JobRecommendation

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'posted_by', 'city', 'state', 'job_type', 'is_active', 'created_at']
    list_filter = ['job_type', 'remote_type', 'is_active', 'visa_sponsorship', 'created_at']
    search_fields = ['title', 'company', 'city', 'required_skills']
    readonly_fields = ['created_at', 'updated_at']

    actions = ['approve_jobs', 'reject_jobs']

    def approve_jobs(self, request, queryset):
        updated = queryset.update(moderation_status='approved', moderation_reason='')
        self.message_user(request, f'{updated} job(s) approved.')
    approve_jobs.short_description = 'Mark selected jobs as Approved'

    def reject_jobs(self, request, queryset):
        # For simplicity, set moderation_status to rejected and add generic reason
        updated = queryset.update(moderation_status='rejected')
        self.message_user(request, f'{updated} job(s) rejected.')
    reject_jobs.short_description = 'Mark selected jobs as Rejected'

    def moderation_display(self, obj):
        color = {'approved': 'green', 'pending': 'orange', 'rejected': 'red'}.get(obj.moderation_status, 'black')
        return format_html('<span style="color: {}">{}</span>', color, obj.get_moderation_status_display())

    moderation_display.short_description = 'Moderation'
    list_display.append('moderation_display')


@admin.register(JobRecommendation)
class JobRecommendationAdmin(admin.ModelAdmin):
    list_display = ['job', 'applicant', 'match_score', 'is_viewed', 'is_applied', 'is_dismissed', 'created_at']
    search_fields = ['job__title', 'applicant__username', 'matched_skills']
    readonly_fields = ['created_at', 'updated_at']
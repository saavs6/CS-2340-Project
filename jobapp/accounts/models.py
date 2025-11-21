from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin

class UserProfile(models.Model):
    USER_TYPE_CHOICES = [
        ('applicant', 'I\'m looking for a job'),
        ('recruiter', 'I\'m looking to hire'),
        ('admin', 'Administrator'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='applicant'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_user_type_display()}"

    def is_job_seeker(self):
        """Check if user is a job seeker/applicant"""
        return self.user_type == 'applicant'

    def is_recruiter(self):
        """Check if user is a recruiter"""
        return self.user_type == 'recruiter'

    def is_admin(self):
        """Check if user is an admin (by role, staff status, or superuser status)"""
        return self.user_type == 'admin' or self.user.is_staff or self.user.is_superuser

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_type', 'created_at']
    list_filter = ['user_type', 'created_at']
    search_fields = ['user__username', 'user__email']
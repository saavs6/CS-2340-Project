from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.models import User
from jobs.models import Job, JobApplication
from applicants.models import ApplicantProfile
from recruiters.models import RecruiterProfile
import csv
from datetime import datetime

def index(request):
    template_data = {}
    template_data['title'] = 'LinkedOut - Your Ticket to Unlimited Jobs!'

    # Check if user is logged in and has a profile
    if request.user.is_authenticated:
        # Check if admin/staff first
        if request.user.is_staff or request.user.is_superuser:
            template_data['user_type'] = 'admin'
            template_data['is_applicant'] = False
            template_data['is_recruiter'] = False
            template_data['is_admin'] = True
        else:
            try:
                profile = request.user.userprofile
                template_data['user_type'] = profile.user_type
                template_data['is_applicant'] = profile.user_type == 'applicant'
                template_data['is_recruiter'] = profile.user_type == 'recruiter'
                template_data['is_admin'] = False

                # Redirect recruiters to their dashboard
                if profile.user_type == 'recruiter':
                    return redirect('recruiters:dashboard')
            except:
                template_data['user_type'] = None
                template_data['is_applicant'] = False
                template_data['is_recruiter'] = False
                template_data['is_admin'] = False
    else:
        template_data['user_type'] = None
        template_data['is_applicant'] = False
        template_data['is_recruiter'] = False
        template_data['is_admin'] = False

    return render(request, 'home/index.html', {
        'template_data': template_data})

def about(request):
    template_data = {}
    template_data['title'] = 'About'

    # Check if user is logged in and has a profile
    if request.user.is_authenticated:
        # Check if admin/staff first
        if request.user.is_staff or request.user.is_superuser:
            template_data['user_type'] = 'admin'
            template_data['is_applicant'] = False
            template_data['is_recruiter'] = False
            template_data['is_admin'] = True
        else:
            try:
                profile = request.user.userprofile
                template_data['user_type'] = profile.user_type
                template_data['is_applicant'] = profile.user_type == 'applicant'
                template_data['is_recruiter'] = profile.user_type == 'recruiter'
                template_data['is_admin'] = False
            except:
                template_data['user_type'] = None
                template_data['is_applicant'] = False
                template_data['is_recruiter'] = False
                template_data['is_admin'] = False
    else:
        template_data['user_type'] = None
        template_data['is_applicant'] = False
        template_data['is_recruiter'] = False
        template_data['is_admin'] = False

    return render(request,
                  'home/about.html',
                  {'template_data': template_data})

@login_required
def admin_dashboard(request):
    """Admin dashboard for data export and management"""
    # Check if user is admin
    if not (request.user.is_staff or request.user.is_superuser):
        return HttpResponseForbidden("You do not have permission to access this page.")

    template_data = {
        'title': 'Admin Dashboard',
        'is_admin': True,
        'user_type': 'admin'
    }

    # Get statistics for display
    template_data['total_users'] = User.objects.count()
    template_data['total_applicants'] = ApplicantProfile.objects.count()
    template_data['total_recruiters'] = RecruiterProfile.objects.count()
    template_data['total_jobs'] = Job.objects.count()
    template_data['total_applications'] = JobApplication.objects.count()

    return render(request, 'home/admin_dashboard.html', {'template_data': template_data})

@login_required
def export_csv(request):
    """Export data as CSV based on export type and filters"""
    # Check if user is admin
    if not (request.user.is_staff or request.user.is_superuser):
        return HttpResponseForbidden("You do not have permission to access this page.")

    export_type = request.GET.get('export_type', 'users')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    # Parse dates if provided
    start_date_obj = None
    end_date_obj = None
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        except ValueError:
            pass
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            pass

    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f"{export_type}_{timestamp}.csv"

    # Create HTTP response with CSV content type
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)

    # Export based on type
    if export_type == 'users':
        # Export all users
        writer.writerow(['ID', 'Username', 'Email', 'First Name', 'Last Name', 'User Type', 'Date Joined', 'Last Login', 'Is Active', 'Is Staff'])
        users = User.objects.all()
        if start_date_obj:
            users = users.filter(date_joined__gte=start_date_obj)
        if end_date_obj:
            users = users.filter(date_joined__lte=end_date_obj)

        for user in users:
            # Get user type from profile
            user_type = ''
            try:
                user_type = user.userprofile.user_type
            except:
                if user.is_staff or user.is_superuser:
                    user_type = 'admin'
                else:
                    user_type = 'unknown'

            writer.writerow([
                user.id,
                user.username,
                user.email,
                user.first_name,
                user.last_name,
                user_type,
                user.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
                user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else 'Never',
                'Yes' if user.is_active else 'No',
                'Yes' if user.is_staff else 'No'
            ])

    elif export_type == 'applications':
        # Export job applications
        writer.writerow(['Application ID', 'Job ID', 'Job Title', 'Company', 'Applicant Username', 'Applicant Email', 'Status', 'Kanban Status', 'Applied Date', 'Last Updated'])
        applications = JobApplication.objects.select_related('job', 'applicant').all()
        if start_date_obj:
            applications = applications.filter(applied_at__gte=start_date_obj)
        if end_date_obj:
            applications = applications.filter(applied_at__lte=end_date_obj)

        for app in applications:
            writer.writerow([
                app.id,
                app.job.id,
                app.job.title,
                app.job.company,
                app.applicant.username,
                app.applicant.email,
                app.get_status_display(),
                app.get_kanban_display_status(),
                app.applied_at.strftime('%Y-%m-%d %H:%M:%S'),
                app.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            ])

    elif export_type == 'jobs':
        # Export job postings
        writer.writerow(['Job ID', 'Title', 'Company', 'Posted By', 'Job Type', 'Remote Type', 'Experience Level', 'City', 'State', 'Country', 'Salary Min', 'Salary Max', 'Is Active', 'Moderation Status', 'Created Date', 'Updated Date'])
        jobs = Job.objects.select_related('posted_by').all()
        if start_date_obj:
            jobs = jobs.filter(created_at__gte=start_date_obj)
        if end_date_obj:
            jobs = jobs.filter(created_at__lte=end_date_obj)

        for job in jobs:
            writer.writerow([
                job.id,
                job.title,
                job.company,
                job.posted_by.username,
                job.get_job_type_display(),
                job.get_remote_type_display(),
                job.get_experience_level_display(),
                job.city,
                job.state,
                job.country,
                job.salary_min if job.salary_min else '',
                job.salary_max if job.salary_max else '',
                'Yes' if job.is_active else 'No',
                job.get_moderation_status_display(),
                job.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                job.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            ])

    elif export_type == 'applicants':
        # Export applicant profiles
        writer.writerow(['Username', 'Email', 'Headline', 'City', 'State', 'Country', 'Skills', 'Remote Work Preference', 'Is Seeking Jobs', 'Is Public', 'Created Date', 'Updated Date'])
        profiles = ApplicantProfile.objects.select_related('user').all()
        if start_date_obj:
            profiles = profiles.filter(created_at__gte=start_date_obj)
        if end_date_obj:
            profiles = profiles.filter(created_at__lte=end_date_obj)

        for profile in profiles:
            writer.writerow([
                profile.user.username,
                profile.user.email,
                profile.headline,
                profile.city,
                profile.state,
                profile.country,
                profile.skills,
                profile.get_remote_work_preference_display(),
                'Yes' if profile.is_seeking_jobs else 'No',
                'Yes' if profile.is_public else 'No',
                profile.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                profile.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            ])

    elif export_type == 'recruiters':
        # Export recruiter profiles
        writer.writerow(['Username', 'Email', 'Company Name', 'Industry', 'Company Size', 'City', 'State', 'Country', 'Website', 'Created Date', 'Updated Date'])
        profiles = RecruiterProfile.objects.select_related('user').all()
        if start_date_obj:
            profiles = profiles.filter(created_at__gte=start_date_obj)
        if end_date_obj:
            profiles = profiles.filter(created_at__lte=end_date_obj)

        for profile in profiles:
            writer.writerow([
                profile.user.username,
                profile.user.email,
                profile.company_name,
                profile.industry,
                profile.get_company_size_display(),
                profile.city,
                profile.state,
                profile.country,
                profile.website,
                profile.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                profile.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            ])

    return response

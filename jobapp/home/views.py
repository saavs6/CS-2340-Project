from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from accounts.models import UserProfile
from .decorators import admin_required
from jobs.models import Job, JobApplication
from applicants.models import ApplicantProfile
from recruiters.models import RecruiterProfile
import csv
from datetime import datetime, timedelta
from django.db.models import Count, Avg, Q, Max, Min
from django.utils import timezone
from collections import defaultdict, Counter

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
        # ENHANCED: Export job applications with full context
        writer.writerow([
            'Application ID', 'Applied Date', 'Last Updated', 'Days Since Applied',
            'Status', 'Kanban Status',
            'Job ID', 'Job Title', 'Company', 'Job Type', 'Remote Type', 'Experience Level',
            'Job Location (City)', 'Job Location (State)', 'Job Location (Country)',
            'Job Salary Min', 'Job Salary Max', 'Job Created Date', 'Job Is Active',
            'Applicant Username', 'Applicant Email', 'Applicant First Name', 'Applicant Last Name',
            'Applicant City', 'Applicant State', 'Applicant Country',
            'Applicant Skills', 'Applicant Remote Preference', 'Applicant Seeking Jobs',
            'Recruiter Username', 'Recruiter Email', 'Recruiter Company'
        ])

        applications = JobApplication.objects.select_related('job', 'applicant', 'job__posted_by').all()
        if start_date_obj:
            applications = applications.filter(applied_at__gte=start_date_obj)
        if end_date_obj:
            applications = applications.filter(applied_at__lte=end_date_obj)

        for app in applications:
            # Get applicant profile data
            applicant_city = applicant_state = applicant_country = applicant_skills = applicant_remote = ''
            applicant_seeking = 'Unknown'
            try:
                ap_profile = app.applicant.applicant_profile
                applicant_city = ap_profile.city
                applicant_state = ap_profile.state
                applicant_country = ap_profile.country
                applicant_skills = ap_profile.skills
                applicant_remote = ap_profile.get_remote_work_preference_display()
                applicant_seeking = 'Yes' if ap_profile.is_seeking_jobs else 'No'
            except:
                pass

            # Get recruiter data
            recruiter_company = ''
            try:
                rec_profile = app.job.posted_by.recruiter_profile
                recruiter_company = rec_profile.company_name
            except:
                pass

            # Calculate days since applied
            days_since_applied = (timezone.now() - app.applied_at).days

            writer.writerow([
                app.id,
                app.applied_at.strftime('%Y-%m-%d %H:%M:%S'),
                app.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                days_since_applied,
                app.get_status_display(),
                app.get_kanban_display_status(),
                app.job.id,
                app.job.title,
                app.job.company,
                app.job.get_job_type_display(),
                app.job.get_remote_type_display(),
                app.job.get_experience_level_display(),
                app.job.city,
                app.job.state,
                app.job.country,
                app.job.salary_min if app.job.salary_min else '',
                app.job.salary_max if app.job.salary_max else '',
                app.job.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'Yes' if app.job.is_active else 'No',
                app.applicant.username,
                app.applicant.email,
                app.applicant.first_name,
                app.applicant.last_name,
                applicant_city,
                applicant_state,
                applicant_country,
                applicant_skills,
                applicant_remote,
                applicant_seeking,
                app.job.posted_by.username,
                app.job.posted_by.email,
                recruiter_company
            ])

    elif export_type == 'jobs':
        # ENHANCED: Export job postings with performance metrics
        writer.writerow([
            'Job ID', 'Title', 'Company', 'Description Length', 'Requirements Length',
            'Job Type', 'Remote Type', 'Experience Level',
            'City', 'State', 'Country', 'Has Coordinates', 'Latitude', 'Longitude',
            'Salary Min', 'Salary Max', 'Salary Currency', 'Salary Period',
            'Required Skills', 'Preferred Skills', 'Visa Sponsorship',
            'Is Active', 'Moderation Status', 'Moderation Reason',
            'Created Date', 'Updated Date', 'Days Since Posted',
            'Posted By Username', 'Posted By Email', 'Recruiter Company', 'Recruiter Industry',
            'Total Applications', 'Applications - Applied', 'Applications - Under Review',
            'Applications - Interview', 'Applications - Offer', 'Applications - Accepted',
            'Applications - Rejected', 'Applications - Withdrawn',
            'Application Rate (per day)', 'Most Recent Application Date'
        ])

        jobs = Job.objects.select_related('posted_by').all()
        if start_date_obj:
            jobs = jobs.filter(created_at__gte=start_date_obj)
        if end_date_obj:
            jobs = jobs.filter(created_at__lte=end_date_obj)

        for job in jobs:
            # Get recruiter info
            recruiter_company = recruiter_industry = ''
            try:
                rec_profile = job.posted_by.recruiter_profile
                recruiter_company = rec_profile.company_name
                recruiter_industry = rec_profile.industry
            except:
                pass

            # Get application statistics
            apps = job.applications.all()
            total_apps = apps.count()
            apps_applied = apps.filter(status='applied').count()
            apps_review = apps.filter(status='review').count()
            apps_interview = apps.filter(status='interview').count()
            apps_offer = apps.filter(status='offer').count()
            apps_accepted = apps.filter(status='accepted').count()
            apps_rejected = apps.filter(status='rejected').count()
            apps_withdrawn = apps.filter(status='withdrawn').count()

            # Calculate days since posted and application rate
            days_since_posted = (timezone.now() - job.created_at).days
            if days_since_posted == 0:
                days_since_posted = 1  # Avoid division by zero
            app_rate = total_apps / days_since_posted if total_apps > 0 else 0

            # Most recent application
            most_recent_app = apps.order_by('-applied_at').first()
            most_recent_app_date = most_recent_app.applied_at.strftime('%Y-%m-%d %H:%M:%S') if most_recent_app else 'No applications'

            writer.writerow([
                job.id,
                job.title,
                job.company,
                len(job.description),
                len(job.requirements),
                job.get_job_type_display(),
                job.get_remote_type_display(),
                job.get_experience_level_display(),
                job.city,
                job.state,
                job.country,
                'Yes' if job.has_coordinates() else 'No',
                job.latitude if job.latitude else '',
                job.longitude if job.longitude else '',
                job.salary_min if job.salary_min else '',
                job.salary_max if job.salary_max else '',
                job.salary_currency,
                job.get_salary_period_display(),
                job.required_skills,
                job.preferred_skills,
                'Yes' if job.visa_sponsorship else 'No',
                'Yes' if job.is_active else 'No',
                job.get_moderation_status_display(),
                job.moderation_reason,
                job.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                job.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                days_since_posted,
                job.posted_by.username,
                job.posted_by.email,
                recruiter_company,
                recruiter_industry,
                total_apps,
                apps_applied,
                apps_review,
                apps_interview,
                apps_offer,
                apps_accepted,
                apps_rejected,
                apps_withdrawn,
                f'{app_rate:.2f}',
                most_recent_app_date
            ])

    elif export_type == 'applicants':
        # ENHANCED: Export applicant profiles with engagement metrics
        writer.writerow([
            'Username', 'Email', 'First Name', 'Last Name', 'User Date Joined', 'Last Login',
            'Headline', 'Summary Length',
            'City', 'State', 'Country', 'Postal Code', 'Has Coordinates', 'Latitude', 'Longitude',
            'Willing to Relocate', 'Remote Work Preference',
            'Skills', 'Number of Skills',
            'LinkedIn URL', 'GitHub URL', 'Portfolio URL', 'Other URL',
            'Is Public', 'Is Seeking Jobs',
            'Profile Created Date', 'Profile Updated Date', 'Days Since Profile Created',
            'Total Applications', 'Applications - Applied', 'Applications - Under Review',
            'Applications - Interview', 'Applications - Offer', 'Applications - Accepted',
            'Applications - Rejected', 'Applications - Withdrawn',
            'Most Recent Application Date', 'Application Frequency (per week)'
        ])

        profiles = ApplicantProfile.objects.select_related('user').all()
        if start_date_obj:
            profiles = profiles.filter(created_at__gte=start_date_obj)
        if end_date_obj:
            profiles = profiles.filter(created_at__lte=end_date_obj)

        for profile in profiles:
            # Count skills
            skills_list = profile.get_skills_list()
            num_skills = len(skills_list)

            # Get application statistics
            apps = profile.user.job_applications.all()
            total_apps = apps.count()
            apps_applied = apps.filter(status='applied').count()
            apps_review = apps.filter(status='review').count()
            apps_interview = apps.filter(status='interview').count()
            apps_offer = apps.filter(status='offer').count()
            apps_accepted = apps.filter(status='accepted').count()
            apps_rejected = apps.filter(status='rejected').count()
            apps_withdrawn = apps.filter(status='withdrawn').count()

            # Most recent application
            most_recent_app = apps.order_by('-applied_at').first()
            most_recent_app_date = most_recent_app.applied_at.strftime('%Y-%m-%d %H:%M:%S') if most_recent_app else 'No applications'

            # Calculate application frequency (applications per week)
            days_since_created = (timezone.now() - profile.created_at).days
            if days_since_created == 0:
                days_since_created = 1
            weeks_since_created = days_since_created / 7
            app_frequency = total_apps / weeks_since_created if weeks_since_created > 0 else 0

            writer.writerow([
                profile.user.username,
                profile.user.email,
                profile.user.first_name,
                profile.user.last_name,
                profile.user.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
                profile.user.last_login.strftime('%Y-%m-%d %H:%M:%S') if profile.user.last_login else 'Never',
                profile.headline,
                len(profile.summary),
                profile.city,
                profile.state,
                profile.country,
                profile.postal_code,
                'Yes' if profile.has_coordinates() else 'No',
                profile.latitude if profile.latitude else '',
                profile.longitude if profile.longitude else '',
                'Yes' if profile.willing_to_relocate else 'No',
                profile.get_remote_work_preference_display(),
                profile.skills,
                num_skills,
                profile.linkedin_url,
                profile.github_url,
                profile.portfolio_url,
                profile.other_url,
                'Yes' if profile.is_public else 'No',
                'Yes' if profile.is_seeking_jobs else 'No',
                profile.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                profile.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                days_since_created,
                total_apps,
                apps_applied,
                apps_review,
                apps_interview,
                apps_offer,
                apps_accepted,
                apps_rejected,
                apps_withdrawn,
                most_recent_app_date,
                f'{app_frequency:.2f}'
            ])

    elif export_type == 'recruiters':
        # ENHANCED: Export recruiter profiles with hiring metrics
        writer.writerow([
            'Username', 'Email', 'First Name', 'Last Name', 'User Date Joined', 'Last Login',
            'Company Name', 'Industry', 'Company Size', 'Company Description Length',
            'City', 'State', 'Country', 'Phone', 'Website',
            'Profile Created Date', 'Profile Updated Date', 'Days Since Profile Created',
            'Total Jobs Posted', 'Active Jobs', 'Inactive Jobs',
            'Jobs - Pending Moderation', 'Jobs - Approved', 'Jobs - Rejected',
            'Total Applications Received', 'Applications - Applied', 'Applications - Under Review',
            'Applications - Interview', 'Applications - Offer', 'Applications - Accepted',
            'Applications - Rejected', 'Applications - Withdrawn',
            'Average Applications per Job', 'Most Recent Job Posted Date'
        ])

        profiles = RecruiterProfile.objects.select_related('user').all()
        if start_date_obj:
            profiles = profiles.filter(created_at__gte=start_date_obj)
        if end_date_obj:
            profiles = profiles.filter(created_at__lte=end_date_obj)

        for profile in profiles:
            # Get job statistics
            jobs = profile.user.posted_jobs.all()
            total_jobs = jobs.count()
            active_jobs = jobs.filter(is_active=True).count()
            inactive_jobs = jobs.filter(is_active=False).count()
            jobs_pending = jobs.filter(moderation_status='pending').count()
            jobs_approved = jobs.filter(moderation_status='approved').count()
            jobs_rejected = jobs.filter(moderation_status='rejected').count()

            # Most recent job
            most_recent_job = jobs.order_by('-created_at').first()
            most_recent_job_date = most_recent_job.created_at.strftime('%Y-%m-%d %H:%M:%S') if most_recent_job else 'No jobs posted'

            # Get application statistics across all jobs
            all_apps = JobApplication.objects.filter(job__posted_by=profile.user)
            total_apps = all_apps.count()
            apps_applied = all_apps.filter(status='applied').count()
            apps_review = all_apps.filter(status='review').count()
            apps_interview = all_apps.filter(status='interview').count()
            apps_offer = all_apps.filter(status='offer').count()
            apps_accepted = all_apps.filter(status='accepted').count()
            apps_rejected = all_apps.filter(status='rejected').count()
            apps_withdrawn = all_apps.filter(status='withdrawn').count()

            # Average applications per job
            avg_apps_per_job = total_apps / total_jobs if total_jobs > 0 else 0

            # Days since profile created
            days_since_created = (timezone.now() - profile.created_at).days

            writer.writerow([
                profile.user.username,
                profile.user.email,
                profile.user.first_name,
                profile.user.last_name,
                profile.user.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
                profile.user.last_login.strftime('%Y-%m-%d %H:%M:%S') if profile.user.last_login else 'Never',
                profile.company_name,
                profile.industry,
                profile.get_company_size_display(),
                len(profile.company_description),
                profile.city,
                profile.state,
                profile.country,
                profile.phone,
                profile.website,
                profile.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                profile.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                days_since_created,
                total_jobs,
                active_jobs,
                inactive_jobs,
                jobs_pending,
                jobs_approved,
                jobs_rejected,
                total_apps,
                apps_applied,
                apps_review,
                apps_interview,
                apps_offer,
                apps_accepted,
                apps_rejected,
                apps_withdrawn,
                f'{avg_apps_per_job:.2f}',
                most_recent_job_date
            ])

    elif export_type == 'usage_analytics':
        # NEW: Comprehensive platform usage analytics
        writer.writerow([
            'Metric Category', 'Metric Name', 'Value', 'Description'
        ])

        # Date range info
        if start_date_obj and end_date_obj:
            date_filter_desc = f"From {start_date} to {end_date}"
        elif start_date_obj:
            date_filter_desc = f"From {start_date} onwards"
        elif end_date_obj:
            date_filter_desc = f"Up to {end_date}"
        else:
            date_filter_desc = "All time"

        writer.writerow(['Report Info', 'Date Range', date_filter_desc, 'Date range for this report'])
        writer.writerow(['Report Info', 'Generated At', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'When this report was generated'])
        writer.writerow(['', '', '', ''])  # Blank row

        # User metrics
        users_qs = User.objects.all()
        if start_date_obj:
            users_qs = users_qs.filter(date_joined__gte=start_date_obj)
        if end_date_obj:
            users_qs = users_qs.filter(date_joined__lte=end_date_obj)

        total_users = users_qs.count()
        active_users = users_qs.filter(is_active=True).count()
        staff_users = users_qs.filter(is_staff=True).count()

        writer.writerow(['Users', 'Total Users', total_users, 'Total number of registered users'])
        writer.writerow(['Users', 'Active Users', active_users, 'Users with active status'])
        writer.writerow(['Users', 'Staff/Admin Users', staff_users, 'Users with staff privileges'])

        # User type breakdown
        applicant_count = ApplicantProfile.objects.count()
        recruiter_count = RecruiterProfile.objects.count()
        writer.writerow(['Users', 'Applicants', applicant_count, 'Users with applicant profiles'])
        writer.writerow(['Users', 'Recruiters', recruiter_count, 'Users with recruiter profiles'])
        writer.writerow(['', '', '', ''])  # Blank row

        # Job metrics
        jobs_qs = Job.objects.all()
        if start_date_obj:
            jobs_qs = jobs_qs.filter(created_at__gte=start_date_obj)
        if end_date_obj:
            jobs_qs = jobs_qs.filter(created_at__lte=end_date_obj)

        total_jobs = jobs_qs.count()
        active_jobs = jobs_qs.filter(is_active=True).count()
        jobs_with_apps = jobs_qs.annotate(app_count=Count('applications')).filter(app_count__gt=0).count()
        jobs_without_apps = total_jobs - jobs_with_apps

        writer.writerow(['Jobs', 'Total Jobs Posted', total_jobs, 'All jobs in the system'])
        writer.writerow(['Jobs', 'Active Jobs', active_jobs, 'Jobs currently active'])
        writer.writerow(['Jobs', 'Jobs with Applications', jobs_with_apps, 'Jobs that have received at least one application'])
        writer.writerow(['Jobs', 'Jobs without Applications', jobs_without_apps, 'Jobs with zero applications'])

        # Job moderation metrics
        jobs_pending = jobs_qs.filter(moderation_status='pending').count()
        jobs_approved = jobs_qs.filter(moderation_status='approved').count()
        jobs_rejected = jobs_qs.filter(moderation_status='rejected').count()
        writer.writerow(['Jobs', 'Jobs - Pending Moderation', jobs_pending, 'Jobs awaiting admin review'])
        writer.writerow(['Jobs', 'Jobs - Approved', jobs_approved, 'Jobs approved by admin'])
        writer.writerow(['Jobs', 'Jobs - Rejected', jobs_rejected, 'Jobs rejected by admin'])
        writer.writerow(['', '', '', ''])  # Blank row

        # Application metrics
        apps_qs = JobApplication.objects.all()
        if start_date_obj:
            apps_qs = apps_qs.filter(applied_at__gte=start_date_obj)
        if end_date_obj:
            apps_qs = apps_qs.filter(applied_at__lte=end_date_obj)

        total_apps = apps_qs.count()
        apps_applied = apps_qs.filter(status='applied').count()
        apps_review = apps_qs.filter(status='review').count()
        apps_interview = apps_qs.filter(status='interview').count()
        apps_offer = apps_qs.filter(status='offer').count()
        apps_accepted = apps_qs.filter(status='accepted').count()
        apps_rejected = apps_qs.filter(status='rejected').count()
        apps_withdrawn = apps_qs.filter(status='withdrawn').count()

        writer.writerow(['Applications', 'Total Applications', total_apps, 'All job applications submitted'])
        writer.writerow(['Applications', 'Applications - Applied', apps_applied, 'Applications in initial applied state'])
        writer.writerow(['Applications', 'Applications - Under Review', apps_review, 'Applications under review'])
        writer.writerow(['Applications', 'Applications - Interview', apps_interview, 'Applications in interview stage'])
        writer.writerow(['Applications', 'Applications - Offer', apps_offer, 'Applications with offers extended'])
        writer.writerow(['Applications', 'Applications - Accepted', apps_accepted, 'Applications where offer was accepted'])
        writer.writerow(['Applications', 'Applications - Rejected', apps_rejected, 'Applications that were rejected'])
        writer.writerow(['Applications', 'Applications - Withdrawn', apps_withdrawn, 'Applications withdrawn by applicant'])

        # Conversion metrics
        if total_apps > 0:
            interview_rate = (apps_interview / total_apps) * 100
            offer_rate = (apps_offer / total_apps) * 100
            acceptance_rate = (apps_accepted / total_apps) * 100
            rejection_rate = (apps_rejected / total_apps) * 100
        else:
            interview_rate = offer_rate = acceptance_rate = rejection_rate = 0

        writer.writerow(['Applications', 'Interview Rate (%)', f'{interview_rate:.2f}', 'Percentage of applications reaching interview'])
        writer.writerow(['Applications', 'Offer Rate (%)', f'{offer_rate:.2f}', 'Percentage of applications receiving offers'])
        writer.writerow(['Applications', 'Acceptance Rate (%)', f'{acceptance_rate:.2f}', 'Percentage of applications accepted'])
        writer.writerow(['Applications', 'Rejection Rate (%)', f'{rejection_rate:.2f}', 'Percentage of applications rejected'])
        writer.writerow(['', '', '', ''])  # Blank row

        # Average metrics
        if total_jobs > 0:
            avg_apps_per_job = total_apps / total_jobs
        else:
            avg_apps_per_job = 0

        if applicant_count > 0:
            avg_apps_per_applicant = total_apps / applicant_count
        else:
            avg_apps_per_applicant = 0

        writer.writerow(['Averages', 'Avg Applications per Job', f'{avg_apps_per_job:.2f}', 'Average number of applications each job receives'])
        writer.writerow(['Averages', 'Avg Applications per Applicant', f'{avg_apps_per_applicant:.2f}', 'Average number of applications each applicant submits'])

    elif export_type == 'skills_analysis':
        # NEW: Skills demand and supply analysis
        writer.writerow(['Skill', 'Jobs Requiring (Count)', 'Jobs Preferring (Count)', 'Total Job Demand', 'Applicants with Skill (Count)', 'Supply vs Demand Ratio'])

        # Collect all skills from jobs and applicants
        job_skills_required = defaultdict(int)
        job_skills_preferred = defaultdict(int)
        applicant_skills = defaultdict(int)

        # Filter jobs by date if needed
        jobs_qs = Job.objects.all()
        if start_date_obj:
            jobs_qs = jobs_qs.filter(created_at__gte=start_date_obj)
        if end_date_obj:
            jobs_qs = jobs_qs.filter(created_at__lte=end_date_obj)

        # Count required and preferred skills in jobs
        for job in jobs_qs:
            for skill in job.get_required_skills_list():
                if skill:
                    job_skills_required[skill.lower()] += 1
            for skill in job.get_preferred_skills_list():
                if skill:
                    job_skills_preferred[skill.lower()] += 1

        # Filter applicants by date if needed
        applicants_qs = ApplicantProfile.objects.all()
        if start_date_obj:
            applicants_qs = applicants_qs.filter(created_at__gte=start_date_obj)
        if end_date_obj:
            applicants_qs = applicants_qs.filter(created_at__lte=end_date_obj)

        # Count skills in applicant profiles
        for applicant in applicants_qs:
            for skill in applicant.get_skills_list():
                if skill:
                    applicant_skills[skill.lower()] += 1

        # Combine all unique skills
        all_skills = set(job_skills_required.keys()) | set(job_skills_preferred.keys()) | set(applicant_skills.keys())

        # Sort by total demand (required + preferred)
        skills_data = []
        for skill in all_skills:
            required_count = job_skills_required.get(skill, 0)
            preferred_count = job_skills_preferred.get(skill, 0)
            total_demand = required_count + preferred_count
            supply_count = applicant_skills.get(skill, 0)

            # Calculate supply vs demand ratio
            if total_demand > 0:
                supply_demand_ratio = supply_count / total_demand
            else:
                supply_demand_ratio = 0

            skills_data.append((skill, required_count, preferred_count, total_demand, supply_count, supply_demand_ratio))

        # Sort by total demand descending
        skills_data.sort(key=lambda x: x[3], reverse=True)

        # Write sorted skills data
        for skill, req, pref, total_demand, supply, ratio in skills_data:
            writer.writerow([skill.title(), req, pref, total_demand, supply, f'{ratio:.2f}'])

    elif export_type == 'daily_trends':
        # NEW: Daily registration and activity trends
        writer.writerow(['Date', 'New Users', 'New Applicants', 'New Recruiters', 'New Jobs Posted', 'New Applications'])

        # Determine date range
        if not start_date_obj:
            # Default to last 90 days if no start date
            start_date_obj = timezone.now() - timedelta(days=90)
        if not end_date_obj:
            end_date_obj = timezone.now()

        # Generate daily statistics
        current_date = start_date_obj.date()
        end_date = end_date_obj.date()

        while current_date <= end_date:
            next_date = current_date + timedelta(days=1)

            # Count new users
            new_users = User.objects.filter(
                date_joined__gte=current_date,
                date_joined__lt=next_date
            ).count()

            # Count new applicant profiles
            new_applicants = ApplicantProfile.objects.filter(
                created_at__gte=current_date,
                created_at__lt=next_date
            ).count()

            # Count new recruiter profiles
            new_recruiters = RecruiterProfile.objects.filter(
                created_at__gte=current_date,
                created_at__lt=next_date
            ).count()

            # Count new jobs
            new_jobs = Job.objects.filter(
                created_at__gte=current_date,
                created_at__lt=next_date
            ).count()

            # Count new applications
            new_apps = JobApplication.objects.filter(
                applied_at__gte=current_date,
                applied_at__lt=next_date
            ).count()

            writer.writerow([
                current_date.strftime('%Y-%m-%d'),
                new_users,
                new_applicants,
                new_recruiters,
                new_jobs,
                new_apps
            ])

            current_date = next_date

    elif export_type == 'geographic_analysis':
        # NEW: Geographic distribution analysis
        writer.writerow(['Type', 'City', 'State', 'Country', 'Count'])

        # Job locations
        jobs_qs = Job.objects.all()
        if start_date_obj:
            jobs_qs = jobs_qs.filter(created_at__gte=start_date_obj)
        if end_date_obj:
            jobs_qs = jobs_qs.filter(created_at__lte=end_date_obj)

        job_locations = jobs_qs.values('city', 'state', 'country').annotate(count=Count('id')).order_by('-count')
        for loc in job_locations:
            writer.writerow(['Job', loc['city'], loc['state'], loc['country'], loc['count']])

        # Applicant locations
        applicants_qs = ApplicantProfile.objects.all()
        if start_date_obj:
            applicants_qs = applicants_qs.filter(created_at__gte=start_date_obj)
        if end_date_obj:
            applicants_qs = applicants_qs.filter(created_at__lte=end_date_obj)

        applicant_locations = applicants_qs.values('city', 'state', 'country').annotate(count=Count('id')).order_by('-count')
        for loc in applicant_locations:
            writer.writerow(['Applicant', loc['city'], loc['state'], loc['country'], loc['count']])

        # Recruiter locations
        recruiters_qs = RecruiterProfile.objects.all()
        if start_date_obj:
            recruiters_qs = recruiters_qs.filter(created_at__gte=start_date_obj)
        if end_date_obj:
            recruiters_qs = recruiters_qs.filter(created_at__lte=end_date_obj)

        recruiter_locations = recruiters_qs.values('city', 'state', 'country').annotate(count=Count('id')).order_by('-count')
        for loc in recruiter_locations:
            writer.writerow(['Recruiter', loc['city'], loc['state'], loc['country'], loc['count']])

    return response


@admin_required
def admin_user_list(request):
    """Admin view to list and manage all users"""
    template_data = {}
    template_data['title'] = 'User Management'
    template_data['is_admin'] = True
    template_data['user_type'] = 'admin'

    # Get search query if provided
    search_query = request.GET.get('search', '').strip()
    role_filter = request.GET.get('role', '').strip()
    status_filter = request.GET.get('status', '').strip()

    # Get all users
    users = User.objects.all().select_related('userprofile').order_by('-date_joined')

    # Apply search filter
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )

    # Apply role filter
    if role_filter:
        if role_filter == 'staff':
            users = users.filter(Q(is_staff=True) | Q(is_superuser=True))
        else:
            users = users.filter(userprofile__user_type=role_filter)

    # Apply status filter
    if status_filter:
        is_active = status_filter == 'active'
        users = users.filter(is_active=is_active)

    # Paginate results
    paginator = Paginator(users, 20)  # Show 20 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Add profile information for each user
    users_data = []
    for user in page_obj:
        user_data = {
            'user': user,
            'profile': None,
            'user_type': None,
            'user_type_display': 'Unknown',
        }

        # Try to get user profile
        try:
            user_data['profile'] = user.userprofile
            user_data['user_type'] = user.userprofile.user_type
            user_data['user_type_display'] = user.userprofile.get_user_type_display()
        except:
            # If no profile, check if staff/superuser
            if user.is_staff or user.is_superuser:
                user_data['user_type'] = 'admin'
                user_data['user_type_display'] = 'Admin/Staff'

        users_data.append(user_data)

    template_data['users_data'] = users_data
    template_data['page_obj'] = page_obj
    template_data['search_query'] = search_query
    template_data['role_filter'] = role_filter
    template_data['status_filter'] = status_filter
    template_data['user_type_choices'] = UserProfile.USER_TYPE_CHOICES

    return render(request, 'home/admin_user_list.html', {'template_data': template_data})


@admin_required
def admin_edit_user_role(request, user_id):
    """Admin endpoint to edit a user's role"""
    if request.method != 'POST':
        return HttpResponseForbidden("This endpoint only accepts POST requests.")

    user = get_object_or_404(User, id=user_id)
    new_role = request.POST.get('role', '').strip()

    # Validate the new role
    valid_roles = [choice[0] for choice in UserProfile.USER_TYPE_CHOICES]
    if new_role not in valid_roles:
        messages.error(request, f"Invalid role: {new_role}")
        return redirect('home.admin_user_list')

    # Get or create UserProfile
    try:
        profile = user.userprofile
        old_role = profile.user_type
        profile.user_type = new_role
        profile.save()
    except UserProfile.DoesNotExist:
        # Create new profile if it doesn't exist
        profile = UserProfile.objects.create(user=user, user_type=new_role)
        old_role = 'none'

    # If changing to admin, grant staff privileges
    if new_role == 'admin' and not user.is_staff:
        user.is_staff = True
        user.save()

    messages.success(request, f"User {user.username}'s role changed from {old_role} to {new_role}")
    return redirect('home.admin_user_list')


@admin_required
def admin_toggle_user_active(request, user_id):
    """Admin endpoint to activate/deactivate a user"""
    if request.method != 'POST':
        return HttpResponseForbidden("This endpoint only accepts POST requests.")

    user = get_object_or_404(User, id=user_id)

    # Prevent admin from deactivating themselves
    if user.id == request.user.id:
        messages.error(request, "You cannot deactivate your own account.")
        return redirect('home.admin_user_list')

    # Toggle active status
    user.is_active = not user.is_active
    user.save()

    status = "activated" if user.is_active else "deactivated"
    messages.success(request, f"User {user.username} has been {status}.")
    return redirect('home.admin_user_list')

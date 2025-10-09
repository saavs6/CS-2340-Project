from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from accounts.decorators import recruiter_required
from applicants.models import ApplicantProfile, Education, WorkExperience
from jobs.models import Job, JobApplication
from .models import RecruiterProfile
from .forms import RecruiterProfileForm, CandidateSearchForm

@recruiter_required
def dashboard(request):
    """Recruiter dashboard - shows hiring features"""
    template_data = {
        'title': 'Hiring Dashboard',
        'user_type': 'recruiter'
    }
    return render(request, 'recruiters/dashboard.html', {
        'template_data': template_data
    })

@recruiter_required
def profile(request):
    """Recruiter profile management"""
    template_data = {
        'title': 'Company Profile',
        'user_type': 'recruiter'
    }
    return render(request, 'recruiters/profile.html', {
        'template_data': template_data
    })

@recruiter_required
def job_postings(request):
    """Manage job postings"""
    template_data = {
        'title': 'Job Postings',
        'user_type': 'recruiter'
    }
    return render(request, 'recruiters/job_postings.html', {
        'template_data': template_data
    })

@recruiter_required
def candidates(request):
    """Search and view candidates"""
    form = CandidateSearchForm(request.GET or None)

    # Start with all public profiles, then apply filters
    candidates = ApplicantProfile.objects.filter(is_public=True)

    # Process search filters
    if request.GET:
        # Keywords search
        keywords = request.GET.get('keywords', '').strip()
        if keywords:
            candidates = candidates.filter(
                Q(user__first_name__icontains=keywords) |
                Q(user__last_name__icontains=keywords) |
                Q(user__username__icontains=keywords) |
                Q(headline__icontains=keywords) |
                Q(summary__icontains=keywords)
            )

        # Skills search
        skills = request.GET.get('skills', '').strip()
        if skills:
            skill_list = [skill.strip() for skill in skills.split(',') if skill.strip()]
            for skill in skill_list:
                candidates = candidates.filter(skills__icontains=skill)

        # Location search
        location = request.GET.get('location', '').strip()
        if location:
            candidates = candidates.filter(
                Q(city__icontains=location) |
                Q(state__icontains=location) |
                Q(country__icontains=location) |
                Q(location__icontains=location)
            )

        # Remote work preference
        remote_preference = request.GET.get('remote_preference')
        if remote_preference:
            candidates = candidates.filter(remote_work_preference=remote_preference)

        # Willing to relocate (only filter if explicitly checked)
        willing_to_relocate = request.GET.get('willing_to_relocate')
        if willing_to_relocate == 'on':  # Checkbox returns 'on' when checked
            candidates = candidates.filter(willing_to_relocate=True)

        # Currently seeking jobs (only filter if explicitly checked)
        is_seeking_jobs = request.GET.get('is_seeking_jobs')
        if is_seeking_jobs == 'on':  # Checkbox returns 'on' when checked
            candidates = candidates.filter(is_seeking_jobs=True)

        # Experience level filter (based on work experience)
        experience_years = request.GET.get('experience_years')
        if experience_years:
            if experience_years == '0-2':
                # Filter for candidates with 0-2 years of experience
                candidates = candidates.annotate(
                    total_experience=Count('work_experience')
                ).filter(
                    Q(work_experience__isnull=True) |  # No work experience
                    Q(work_experience__isnull=False)  # Has work experience but we'll filter by years
                )
                # Additional filtering would need to be done in Python for date calculations
            elif experience_years == '3-5':
                # Similar logic for 3-5 years
                pass
            elif experience_years == '6-10':
                # Similar logic for 6-10 years
                pass
            elif experience_years == '10+':
                # Similar logic for 10+ years
                pass

        # Education level filter
        education_level = request.GET.get('education_level')
        if education_level:
            if education_level == 'high_school':
                candidates = candidates.filter(education__isnull=True)
            elif education_level == 'associate':
                candidates = candidates.filter(education__degree__icontains='associate')
            elif education_level == 'bachelor':
                candidates = candidates.filter(education__degree__icontains="bachelor")
            elif education_level == 'master':
                candidates = candidates.filter(education__degree__icontains="master")
            elif education_level == 'phd':
                candidates = candidates.filter(education__degree__icontains="phd")

    # Order by most recently updated
    candidates = candidates.order_by('-updated_at')

    # Pagination
    paginator = Paginator(candidates, 12)  # Show 12 candidates per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    template_data = {
        'title': 'Find Candidates',
        'user_type': 'recruiter'
    }

    return render(request, 'recruiters/candidates.html', {
        'template_data': template_data,
        'form': form,
        'page_obj': page_obj,
        'candidates_count': candidates.count()
    })

@recruiter_required
def candidate_detail(request, pk):
    """View detailed candidate profile"""
    candidate = get_object_or_404(ApplicantProfile, pk=pk, is_public=True)

    template_data = {
        'title': f'{candidate.user.get_full_name()} - Profile',
        'user_type': 'recruiter'
    }

    return render(request, 'recruiters/candidate_detail.html', {
        'template_data': template_data,
        'candidate': candidate
    })

@recruiter_required
def profile(request):
    """Recruiter profile management"""
    try:
        profile = request.user.recruiter_profile
    except RecruiterProfile.DoesNotExist:
        # Create profile if it doesn't exist
        profile = RecruiterProfile.objects.create(user=request.user)

    if request.method == 'POST':
        form = RecruiterProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('recruiters:profile')
    else:
        form = RecruiterProfileForm(instance=profile)

    template_data = {
        'title': 'Company Profile',
        'user_type': 'recruiter',
        'form': form
    }
    return render(request, 'recruiters/profile.html', {
        'template_data': template_data
    })

@recruiter_required
def job_applications(request, job_id):
    """View applications for a specific job"""
    job = get_object_or_404(Job, pk=job_id, posted_by=request.user)
    applications = JobApplication.objects.filter(job=job).order_by('-applied_at')

    # Group applications by kanban status
    kanban_columns = {
        'applied': applications.filter(kanban_status='applied'),
        'review': applications.filter(kanban_status='review'),
        'interview': applications.filter(kanban_status='interview'),
        'offer': applications.filter(kanban_status='offer'),
        'closed': applications.filter(kanban_status='closed'),
    }

    template_data = {
        'title': f'Applications for {job.title}',
        'user_type': 'recruiter'
    }

    return render(request, 'recruiters/job_applications.html', {
        'template_data': template_data,
        'job': job,
        'kanban_columns': kanban_columns,
        'applications': applications
    })

@recruiter_required
def kanban_board(request, job_id):
    """Kanban board view for managing applications"""
    job = get_object_or_404(Job, pk=job_id, posted_by=request.user)
    applications = JobApplication.objects.filter(job=job).order_by('-applied_at')

    # Group applications by kanban status
    kanban_columns = {
        'applied': applications.filter(kanban_status='applied'),
        'review': applications.filter(kanban_status='review'),
        'interview': applications.filter(kanban_status='interview'),
        'offer': applications.filter(kanban_status='offer'),
        'closed': applications.filter(kanban_status='closed'),
    }

    template_data = {
        'title': f'Manage Applications - {job.title}',
        'user_type': 'recruiter'
    }

    return render(request, 'recruiters/kanban_board.html', {
        'template_data': template_data,
        'job': job,
        'kanban_columns': kanban_columns,
        'applications': applications
    })

@recruiter_required
@require_http_methods(["POST"])
@csrf_exempt
def update_application_status(request):
    """AJAX endpoint to update application status"""
    try:
        data = json.loads(request.body)
        application_id = data.get('application_id')
        new_status = data.get('new_status')

        if not application_id or not new_status:
            return JsonResponse({'success': False, 'error': 'Missing required fields'})

        application = get_object_or_404(JobApplication, pk=application_id, job__posted_by=request.user)

        # Validate the new status
        valid_statuses = [choice[0] for choice in JobApplication.KANBAN_STATUS_CHOICES]
        if new_status not in valid_statuses:
            return JsonResponse({'success': False, 'error': 'Invalid status'})

        # Update the application status
        application.update_kanban_status(new_status)

        return JsonResponse({
            'success': True,
            'new_status': new_status,
            'display_status': application.get_kanban_display_status()
        })

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@recruiter_required
def application_detail(request, application_id):
    """View detailed application information"""
    application = get_object_or_404(JobApplication, pk=application_id, job__posted_by=request.user)
    applicant_profile = get_object_or_404(ApplicantProfile, user=application.applicant)

    template_data = {
        'title': f'Application - {application.applicant.get_full_name()}',
        'user_type': 'recruiter'
    }

    return render(request, 'recruiters/application_detail.html', {
        'template_data': template_data,
        'application': application,
        'applicant_profile': applicant_profile,
        'job': application.job
    })
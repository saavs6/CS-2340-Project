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
from .forms import SavedSearchForm
from .models import SavedSearch
from django.utils import timezone

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

    # Candidate recommendations (from applied candidates only)
    # Build sets of normalized skills from job
    def normalize_skills(skills_list):
        return set([s.strip().lower() for s in skills_list if s and s.strip()])

    required = normalize_skills(job.get_required_skills_list())
    preferred = normalize_skills(job.get_preferred_skills_list())

    recommendations = []

    def remote_bonus(job_remote, applicant_pref):
        mapping = {
            'remote': {'remote_only': 2, 'hybrid': 1, 'flexible': 1, 'onsite_only': 0},
            'hybrid': {'hybrid': 2, 'flexible': 1, 'remote_only': 1, 'onsite_only': 1},
            'onsite': {'onsite_only': 2, 'hybrid': 1, 'flexible': 1, 'remote_only': -3},
        }
        return mapping.get(job_remote, {}).get(applicant_pref, 0)

    # Score only candidates who applied to this job
    applied_applications = applications.select_related('applicant')
    for app in applied_applications:
        # Get applicant profile; skip if not found
        try:
            profile = app.applicant.applicant_profile
        except ApplicantProfile.DoesNotExist:
            continue

        # Normalize applicant skills
        applicant_skills = set()
        if profile.skills:
            applicant_skills = set([s.strip().lower() for s in profile.skills.split(',') if s.strip()])

        matched_required = required & applicant_skills
        matched_preferred = preferred & applicant_skills

        # Base skill score
        score = len(matched_required) * 3 + len(matched_preferred)

        # Location bonus
        if profile.city and profile.state:
            if profile.city.strip().lower() == job.city.strip().lower() and profile.state.strip().lower() == job.state.strip().lower():
                score += 2
            elif profile.state.strip().lower() == job.state.strip().lower():
                score += 1

        # Remote preference bonus/penalty
        score += remote_bonus(job.remote_type, profile.remote_work_preference)

        # If no skills match at all, down-rank significantly
        if not matched_required and not matched_preferred:
            score -= 2

        recommendations.append({
            'profile': profile,
            'score': score,
            'matched_required': sorted(matched_required),
            'matched_preferred': sorted(matched_preferred),
        })

    # Sort and limit
    recommendations.sort(key=lambda x: x['score'], reverse=True)
    recommended_candidates = [r for r in recommendations if r['score'] > 0][:8]

    return render(request, 'recruiters/job_applications.html', {
        'template_data': template_data,
        'job': job,
        'kanban_columns': kanban_columns,
        'applications': applications,
        'recommended_candidates': recommended_candidates,
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


@recruiter_required
def saved_search_list(request):
    """List saved searches for the recruiter"""
    searches = list(SavedSearch.objects.filter(recruiter=request.user).order_by('-created_at'))

    # For each saved search, compute current match count (reuse filtering logic)
    for s in searches:
        qs = ApplicantProfile.objects.filter(is_public=True)
        if s.keywords:
            kw = s.keywords.strip()
            qs = qs.filter(
                Q(user__first_name__icontains=kw) |
                Q(user__last_name__icontains=kw) |
                Q(user__username__icontains=kw) |
                Q(headline__icontains=kw) |
                Q(summary__icontains=kw)
            )
        if s.skills:
            for skill in [sk.strip() for sk in s.skills.split(',') if sk.strip()]:
                qs = qs.filter(skills__icontains=skill)
        if s.location:
            loc = s.location.strip()
            qs = qs.filter(
                Q(city__icontains=loc) | Q(state__icontains=loc) | Q(country__icontains=loc) | Q(location__icontains=loc)
            )
        if s.remote_preference:
            qs = qs.filter(remote_work_preference=s.remote_preference)
        if s.willing_to_relocate:
            qs = qs.filter(willing_to_relocate=True)
        if s.is_seeking_jobs:
            qs = qs.filter(is_seeking_jobs=True)
        # Experience and education are simplified here
        if s.education_level:
            if s.education_level == 'high_school':
                qs = qs.filter(education__isnull=True)
            else:
                qs = qs.filter(education__degree__icontains=s.education_level)

        s.match_count = qs.count()

    template_data = {'title': 'Saved Searches', 'user_type': 'recruiter'}
    return render(request, 'recruiters/saved_search_list.html', {'template_data': template_data, 'searches': searches})


@recruiter_required
def saved_search_create(request):
    """Create a new saved search"""
    if request.method == 'POST':
        form = SavedSearchForm(request.POST)
        if form.is_valid():
            saved = form.save(commit=False)
            saved.recruiter = request.user
            saved.save()
            messages.success(request, 'Saved search created.')
            return redirect('recruiters:saved_search_list')
    else:
        form = SavedSearchForm()
    template_data = {'title': 'Create Saved Search', 'user_type': 'recruiter'}
    return render(request, 'recruiters/saved_search_form.html', {'template_data': template_data, 'form': form})


@recruiter_required
def saved_search_edit(request, pk):
    saved = get_object_or_404(SavedSearch, pk=pk, recruiter=request.user)
    if request.method == 'POST':
        form = SavedSearchForm(request.POST, instance=saved)
        if form.is_valid():
            form.save()
            messages.success(request, 'Saved search updated.')
            return redirect('recruiters:saved_search_list')
    else:
        form = SavedSearchForm(instance=saved)
    template_data = {'title': 'Edit Saved Search', 'user_type': 'recruiter'}
    return render(request, 'recruiters/saved_search_form.html', {'template_data': template_data, 'form': form, 'saved': saved})


@recruiter_required
def saved_search_delete(request, pk):
    saved = get_object_or_404(SavedSearch, pk=pk, recruiter=request.user)
    if request.method == 'POST':
        saved.delete()
        messages.success(request, 'Saved search deleted.')
        return redirect('recruiters:saved_search_list')
    template_data = {'title': 'Delete Saved Search', 'user_type': 'recruiter'}
    return render(request, 'recruiters/saved_search_confirm_delete.html', {'template_data': template_data, 'saved': saved})

@recruiter_required
def saved_search_detail(request, pk):
    saved = get_object_or_404(SavedSearch, pk=pk, recruiter=request.user)
    qs = ApplicantProfile.objects.filter(is_public=True)
    if saved.keywords:
        kw = saved.keywords.strip()
        qs = qs.filter(
            Q(user__first_name__icontains=kw) |
            Q(user__last_name__icontains=kw) |
            Q(user__username__icontains=kw) |
            Q(headline__icontains=kw) |
            Q(summary__icontains=kw)
        )
    if saved.skills:
        for skill in [sk.strip() for sk in saved.skills.split(',') if sk.strip()]:
            qs = qs.filter(skills__icontains=skill)
    if saved.location:
        loc = saved.location.strip()
        qs = qs.filter(
            Q(city__icontains=loc) | Q(state__icontains=loc) | Q(country__icontains=loc) | Q(location__icontains=loc)
        )
    if saved.remote_preference:
        qs = qs.filter(remote_work_preference=saved.remote_preference)
    if saved.willing_to_relocate:
        qs = qs.filter(willing_to_relocate=True)
    if saved.is_seeking_jobs:
        qs = qs.filter(is_seeking_jobs=True)
    if saved.education_level:
        if saved.education_level == 'high_school':
            qs = qs.filter(education__isnull=True)
        else:
            qs = qs.filter(education__degree__icontains=saved.education_level)
    candidates = qs.order_by('-updated_at')
    template_data = {'title': f'Saved Search: {saved.name}', 'user_type': 'recruiter'}
    return render(request, 'recruiters/saved_search_detail.html', {'template_data': template_data, 'saved': saved, 'candidates': candidates})

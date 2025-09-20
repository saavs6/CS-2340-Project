from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from accounts.decorators import recruiter_required, applicant_required
from .models import Job, JobApplication
from .forms import JobForm, JobSearchForm, JobApplicationForm

# Job Listing and Search Views
def job_list(request):
    """Public job listing with search functionality"""
    form = JobSearchForm(request.GET or None)
    jobs = Job.objects.filter(is_active=True)
    
    if form.is_valid():
        # Apply filters
        if form.cleaned_data.get('keywords'):
            keywords = form.cleaned_data['keywords']
            jobs = jobs.filter(
                Q(title__icontains=keywords) |
                Q(company__icontains=keywords) |
                Q(description__icontains=keywords) |
                Q(required_skills__icontains=keywords)
            )
        
        if form.cleaned_data.get('location'):
            location = form.cleaned_data['location']
            jobs = jobs.filter(
                Q(city__icontains=location) |
                Q(state__icontains=location) |
                Q(country__icontains=location)
            )
        
        if form.cleaned_data.get('job_type'):
            jobs = jobs.filter(job_type__in=form.cleaned_data['job_type'])
        
        if form.cleaned_data.get('remote_type'):
            jobs = jobs.filter(remote_type__in=form.cleaned_data['remote_type'])
        
        if form.cleaned_data.get('experience_level'):
            jobs = jobs.filter(experience_level__in=form.cleaned_data['experience_level'])
        
        if form.cleaned_data.get('salary_min'):
            jobs = jobs.filter(salary_min__gte=form.cleaned_data['salary_min'])
        
        if form.cleaned_data.get('visa_sponsorship'):
            jobs = jobs.filter(visa_sponsorship=True)
        
        if form.cleaned_data.get('skills'):
            skills = [skill.strip() for skill in form.cleaned_data['skills'].split(',')]
            for skill in skills:
                jobs = jobs.filter(
                    Q(required_skills__icontains=skill) |
                    Q(preferred_skills__icontains=skill)
                )
    
    # Pagination
    paginator = Paginator(jobs, 10)  # Show 10 jobs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'template_data': {
            'title': 'Find Jobs',
            'user_type': getattr(request.user.userprofile, 'user_type', None) if request.user.is_authenticated else None
        },
        'form': form,
        'page_obj': page_obj,
        'jobs_count': jobs.count()
    }
    
    return render(request, 'jobs/job_list.html', context)

def job_detail(request, pk):
    """Job detail view"""
    job = get_object_or_404(Job, pk=pk, is_active=True)
    
    # Check if user has already applied (for applicants)
    has_applied = False
    if request.user.is_authenticated:
        try:
            if request.user.userprofile.user_type == 'applicant':
                has_applied = JobApplication.objects.filter(
                    job=job, applicant=request.user
                ).exists()
        except:
            pass
    
    context = {
        'template_data': {
            'title': job.title,
            'user_type': getattr(request.user.userprofile, 'user_type', None) if request.user.is_authenticated else None
        },
        'job': job,
        'has_applied': has_applied
    }
    
    return render(request, 'jobs/job_detail.html', context)

# Recruiter Views
@recruiter_required
def job_create(request):
    """Create new job posting"""
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.save()
            messages.success(request, 'Job posted successfully!')
            return redirect('jobs:detail', pk=job.pk)
    else:
        form = JobForm()
    
    context = {
        'template_data': {
            'title': 'Post New Job',
            'user_type': 'recruiter'
        },
        'form': form
    }
    
    return render(request, 'jobs/job_form.html', context)

@recruiter_required
def job_edit(request, pk):
    """Edit existing job posting"""
    job = get_object_or_404(Job, pk=pk, posted_by=request.user)
    
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job updated successfully!')
            return redirect('jobs:detail', pk=job.pk)
    else:
        form = JobForm(instance=job)
    
    context = {
        'template_data': {
            'title': 'Edit Job',
            'user_type': 'recruiter'
        },
        'form': form,
        'job': job
    }
    
    return render(request, 'jobs/job_form.html', context)

@recruiter_required
def recruiter_jobs(request):
    """List recruiter's job postings"""
    jobs = Job.objects.filter(posted_by=request.user).order_by('-created_at')
    
    context = {
        'template_data': {
            'title': 'My Job Postings',
            'user_type': 'recruiter'
        },
        'jobs': jobs
    }
    
    return render(request, 'jobs/recruiter_jobs.html', context)

# Applicant Views
@applicant_required
def job_apply(request, pk):
    """Apply to a job"""
    job = get_object_or_404(Job, pk=pk, is_active=True)
    
    # Check if already applied
    if JobApplication.objects.filter(job=job, applicant=request.user).exists():
        messages.warning(request, 'You have already applied to this job.')
        return redirect('jobs:detail', pk=job.pk)
    
    if request.method == 'POST':
        form = JobApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            messages.success(request, 'Application submitted successfully!')
            return redirect('jobs:detail', pk=job.pk)
    else:
        form = JobApplicationForm()
    
    context = {
        'template_data': {
            'title': f'Apply to {job.title}',
            'user_type': 'applicant'
        },
        'form': form,
        'job': job
    }
    
    return render(request, 'jobs/job_apply.html', context)

@applicant_required
def my_applications(request):
    """View applicant's job applications"""
    applications = JobApplication.objects.filter(applicant=request.user).order_by('-applied_at')
    
    context = {
        'template_data': {
            'title': 'My Applications',
            'user_type': 'applicant'
        },
        'applications': applications
    }
    
    return render(request, 'jobs/my_applications.html', context)
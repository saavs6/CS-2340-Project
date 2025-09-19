from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.decorators import recruiter_required

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
    """View and manage candidates"""
    template_data = {
        'title': 'Candidates',
        'user_type': 'recruiter'
    }
    return render(request, 'recruiters/candidates.html', {
        'template_data': template_data
    })
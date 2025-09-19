from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.decorators import applicant_required

@applicant_required
def dashboard(request):
    """Applicant dashboard - shows job search features"""
    template_data = {
        'title': 'Job Search Dashboard',
        'user_type': 'applicant'
    }
    return render(request, 'applicants/dashboard.html', {
        'template_data': template_data
    })

@applicant_required
def profile(request):
    """Applicant profile management"""
    template_data = {
        'title': 'My Profile',
        'user_type': 'applicant'
    }
    return render(request, 'applicants/profile.html', {
        'template_data': template_data
    })

@applicant_required
def applications(request):
    """View job applications"""
    template_data = {
        'title': 'My Applications',
        'user_type': 'applicant'
    }
    return render(request, 'applicants/applications.html', {
        'template_data': template_data
    })

@applicant_required
def job_search(request):
    """Search for jobs"""
    template_data = {
        'title': 'Find Jobs',
        'user_type': 'applicant'
    }
    return render(request, 'applicants/job_search.html', {
        'template_data': template_data
    })
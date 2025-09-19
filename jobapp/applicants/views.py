from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.forms import inlineformset_factory
from accounts.decorators import applicant_required
from .models import ApplicantProfile, Education, WorkExperience
from .forms import ApplicantProfileForm, EducationForm, WorkExperienceForm

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
    """View applicant profile"""
    try:
        profile = request.user.applicant_profile
    except ApplicantProfile.DoesNotExist:
        # Create profile if it doesn't exist
        profile = ApplicantProfile.objects.create(user=request.user)

    template_data = {
        'title': 'My Profile',
        'user_type': 'applicant',
        'profile': profile
    }
    return render(request, 'applicants/profile.html', {
        'template_data': template_data
    })

@applicant_required
def profile_edit(request):
    """Edit applicant profile"""
    try:
        profile = request.user.applicant_profile
    except ApplicantProfile.DoesNotExist:
        # Create profile if it doesn't exist
        profile = ApplicantProfile.objects.create(user=request.user)

    # Create formsets for education and work experience
    EducationFormSet = inlineformset_factory(
        ApplicantProfile, Education,
        form=EducationForm,
        extra=1,
        can_delete=True
    )
    WorkExperienceFormSet = inlineformset_factory(
        ApplicantProfile, WorkExperience,
        form=WorkExperienceForm,
        extra=1,
        can_delete=True
    )

    if request.method == 'POST':
        profile_form = ApplicantProfileForm(request.POST, instance=profile)
        education_formset = EducationFormSet(request.POST, instance=profile)
        work_formset = WorkExperienceFormSet(request.POST, instance=profile)

        if profile_form.is_valid() and education_formset.is_valid() and work_formset.is_valid():
            profile_form.save()
            education_formset.save()
            work_formset.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('applicants:profile')
    else:
        profile_form = ApplicantProfileForm(instance=profile)
        education_formset = EducationFormSet(instance=profile)
        work_formset = WorkExperienceFormSet(instance=profile)

    template_data = {
        'title': 'Edit Profile',
        'user_type': 'applicant',
        'profile_form': profile_form,
        'education_formset': education_formset,
        'work_formset': work_formset,
    }
    return render(request, 'applicants/profile_edit.html', {
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
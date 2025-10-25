from django.db.models.signals import post_save
from django.dispatch import receiver
from applicants.models import ApplicantProfile
from recruiters.models import SavedSearch
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User

# Utility to check if a profile matches a saved search

def profile_matches_search(profile, search):
    # Keywords
    if search.keywords:
        if not (search.keywords.lower() in (profile.headline or '').lower() or search.keywords.lower() in (profile.summary or '').lower()):
            return False
    # Skills
    if search.skills:
        search_skills = set([s.strip().lower() for s in search.skills.split(',') if s.strip()])
        profile_skills = set([s.strip().lower() for s in profile.get_skills_list()])
        if not search_skills.issubset(profile_skills):
            return False
    # Location
    if search.location:
        if not (search.location.lower() in (profile.location or '').lower()):
            return False
    # Remote preference
    if search.remote_preference and search.remote_preference != '':
        if profile.remote_work_preference != search.remote_preference:
            return False
    # Experience (not implemented in profile, skip for now)
    # Education (not implemented in profile, skip for now)
    # Willing to relocate
    if search.willing_to_relocate and not profile.willing_to_relocate:
        return False
    # Is seeking jobs
    if search.is_seeking_jobs and not profile.is_seeking_jobs:
        return False
    return True

@receiver(post_save, sender=ApplicantProfile)
def notify_recruiters_on_profile_update(sender, instance, created, **kwargs):
    # For each active saved search, check if this profile matches
    searches = SavedSearch.objects.filter(is_active=True)
    for search in searches:
        if profile_matches_search(instance, search):
            # Send notification (email for now)
            recruiter = search.recruiter
            subject = f"New candidate matches your saved search: {search.name}"
            message = f"Candidate {instance.user.get_full_name() or instance.user.username} now matches your saved search '{search.name}'.\n\nView profile: https://yourdomain.com/recruiters/candidate/{instance.user.id}/"
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [recruiter.email],
                fail_silently=True
            )

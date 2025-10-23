from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Q
from applicants.models import ApplicantProfile
from recruiters.models import SavedSearch

import datetime

class Command(BaseCommand):
    help = 'Check saved candidate searches and notify recruiters about new matches'

    def handle(self, *args, **options):
        now = timezone.now()
        searches = SavedSearch.objects.filter(is_active=True)
        for s in searches:
            # Determine when to run based on frequency
            if s.notification_frequency == 'never':
                continue
            if s.last_notified:
                delta = now - s.last_notified
            else:
                # If never notified, behave as if it was long ago
                delta = datetime.timedelta(days=365)

            should_run = False
            if s.notification_frequency == 'daily' and delta >= datetime.timedelta(days=1):
                should_run = True
            elif s.notification_frequency == 'weekly' and delta >= datetime.timedelta(days=7):
                should_run = True
            elif s.notification_frequency == 'monthly' and delta >= datetime.timedelta(days=30):
                should_run = True

            if not should_run:
                continue

            # Build queryset using saved search params
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
            # Note: experience and education filters are simplified
            if s.experience_years:
                # Skip complex experience calculations for now
                pass
            if s.education_level:
                if s.education_level == 'high_school':
                    qs = qs.filter(education__isnull=True)
                else:
                    qs = qs.filter(education__degree__icontains=s.education_level)

            # Count matches
            match_count = qs.count()

            # Decide if we should notify: here we notify if >0 matches
            if match_count > 0:
                # Send email
                subject = f"Saved Search Matches: {s.name}"
                body = f"Your saved search '{s.name}' has {match_count} matching candidates.\n\nVisit your dashboard to review matches."
                recipient = [s.recruiter.email] if s.recruiter.email else None
                if recipient:
                    try:
                        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, recipient)
                        self.stdout.write(self.style.SUCCESS(f"Notified {s.recruiter.email} for saved search '{s.name}' ({match_count} matches)"))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Failed to send email to {s.recruiter.email}: {e}"))
                else:
                    self.stdout.write(self.style.WARNING(f"Recruiter {s.recruiter.username} has no email; skipping email for '{s.name}' ({match_count} matches)"))

            # Update last_notified timestamp
            s.last_notified = now
            s.save(update_fields=['last_notified'])

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from jobs.models import Job, JobRecommendation
from applicants.models import ApplicantProfile
from django.db import transaction
import math
from datetime import timedelta
from django.utils import timezone


def tokenize_skills(text):
    if not text:
        return set()
    parts = [p.strip().lower() for p in text.split(',') if p.strip()]
    tokens = set()
    for p in parts:
        # break multi-word skills into tokens as well (e.g., 'machine learning' -> 'machine','learning')
        tokens.update([t for t in p.replace('/', ' ').split() if t])
        tokens.add(p)
    return tokens


def haversine_km(lat1, lon1, lat2, lon2):
    # returns distance in kilometers
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c


class Command(BaseCommand):
    help = 'Generate job recommendations for applicants using improved matching heuristics'

    def handle(self, *args, **options):
        users = User.objects.filter(is_active=True)
        created = 0
        updated = 0
        skipped = 0

        now = timezone.now()
        new_job_boost_days = 14  # boost jobs created within last N days

        for user in users:
            try:
                profile = user.applicant_profile
            except ApplicantProfile.DoesNotExist:
                continue

            # only generate for applicants who are seeking jobs and have some skills
            if not profile.is_seeking_jobs:
                skipped += 1
                continue

            applicant_skills = tokenize_skills(profile.skills)
            if not applicant_skills:
                skipped += 1
                continue

            # Consider active jobs that the applicant hasn't applied to
            applied_job_ids = set(user.job_applications.values_list('job_id', flat=True))
            jobs = Job.objects.filter(is_active=True).exclude(id__in=applied_job_ids)

            for job in jobs:
                # skip jobs applicant dismissed earlier
                if JobRecommendation.objects.filter(applicant=user, job=job, is_dismissed=True).exists():
                    continue

                required = tokenize_skills(job.required_skills)
                preferred = tokenize_skills(job.preferred_skills)

                # Jaccard-style similarity for combined skill set
                job_skill_set = required.union(preferred)
                if not job_skill_set:
                    # if job has no listed skills, give small default score
                    skills_similarity = 0.0
                else:
                    intersection = applicant_skills.intersection(job_skill_set)
                    union = applicant_skills.union(job_skill_set)
                    skills_similarity = (len(intersection) / max(1, len(union)))

                # reward matching required skills more heavily and penalize missing required skills
                matched_required = applicant_skills.intersection(required)
                missing_required = required.difference(applicant_skills)
                if required:
                    required_coverage = len(matched_required) / len(required)
                else:
                    required_coverage = 0.0

                # base skill score scaled to 0-70
                skills_score = skills_similarity * 70.0
                # add required coverage bonus up to 20
                skills_score += required_coverage * 20.0
                # penalty for each missing required skill (up to -30)
                skills_score -= min(30.0, len(missing_required) * 7.5)

                # location scoring: prefer closer jobs if coordinates present
                location_score = 0.0
                try:
                    if profile.has_coordinates() and job.has_coordinates():
                        ap_lat, ap_lng = profile.get_coordinates()
                        job_lat, job_lng = job.get_coordinates()
                        dist_km = haversine_km(ap_lat, ap_lng, job_lat, job_lng)
                        # score from 0..10 where closer is better; within 50km gets full 10
                        location_score = max(0.0, (50.0 - min(dist_km, 50.0)) / 50.0) * 10.0
                    else:
                        # fallback: same city/country small bonus
                        if profile.country and job.country and profile.country.lower() == job.country.lower():
                            location_score += 3.0
                        if profile.city and job.city and profile.city.lower() == job.city.lower():
                            location_score += 5.0
                except Exception:
                    location_score = 0.0

                # experience match: map job experience to a soft score
                exp_score = 0.0
                if job.experience_level == 'entry':
                    exp_score = 5.0
                elif job.experience_level == 'mid':
                    exp_score = 7.0
                elif job.experience_level == 'senior':
                    exp_score = 4.0

                # recency boost for new jobs
                recency_boost = 0.0
                if hasattr(job, 'created_at') and job.created_at:
                    days = (now - job.created_at).days
                    if days <= new_job_boost_days:
                        recency_boost = max(0.0, (new_job_boost_days - days) / new_job_boost_days) * 5.0

                # compute final score, normalized 0-100
                raw = skills_score + location_score + exp_score + recency_boost
                match_score = max(0.0, min(100.0, raw))

                # ignore very low scores
                if match_score < 12:
                    continue

                matched_skills_list = list(applicant_skills.intersection(job_skill_set))
                missing_skills_list = list(missing_required)

                # create or update JobRecommendation record
                obj, created_flag = JobRecommendation.objects.update_or_create(
                    applicant=user,
                    job=job,
                    defaults={
                        'match_score': match_score,
                        'skills_match_score': round(skills_score, 2),
                        'location_match_score': round(location_score, 2),
                        'experience_match_score': round(exp_score, 2),
                        'matched_skills': ', '.join(sorted(matched_skills_list)),
                        'missing_skills': ', '.join(sorted(missing_skills_list)),
                        'recommendation_reason': f"Matched: {', '.join(sorted(matched_skills_list))}; missing: {', '.join(sorted(missing_skills_list))}",
                    }
                )

                if created_flag:
                    created += 1
                else:
                    updated += 1

        self.stdout.write(self.style.SUCCESS(f'Recommendations created: {created}, updated: {updated}, skipped users: {skipped}'))

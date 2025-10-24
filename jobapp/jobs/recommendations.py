from datetime import timedelta
from django.utils import timezone
import math


def tokenize_skills(text):
    if not text:
        return set()
    parts = [p.strip().lower() for p in text.split(',') if p.strip()]
    tokens = set()
    for p in parts:
        tokens.update([t for t in p.replace('/', ' ').split() if t])
        tokens.add(p)
    return tokens


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c


def generate_recommendations_for_user(user):
    """Generate/update JobRecommendation objects for a single user.

    This is a refactor of the management command logic to allow calling
    recommendation generation programmatically (e.g., from signals).
    """
    # Import models locally to avoid circular imports at module import time
    from django.contrib.auth.models import User
    from jobs.models import Job, JobRecommendation
    from applicants.models import ApplicantProfile

    try:
        profile = user.applicant_profile
    except ApplicantProfile.DoesNotExist:
        return {'created': 0, 'updated': 0, 'skipped': 1}

    if not profile.is_seeking_jobs:
        return {'created': 0, 'updated': 0, 'skipped': 1}

    applicant_skills = tokenize_skills(profile.skills)
    if not applicant_skills:
        return {'created': 0, 'updated': 0, 'skipped': 1}

    created = 0
    updated = 0

    now = timezone.now()
    new_job_boost_days = 14

    applied_job_ids = set(user.job_applications.values_list('job_id', flat=True))
    jobs = Job.objects.filter(is_active=True).exclude(id__in=applied_job_ids)

    for job in jobs:
        if JobRecommendation.objects.filter(applicant=user, job=job, is_dismissed=True).exists():
            continue

        required = tokenize_skills(job.required_skills)
        preferred = tokenize_skills(job.preferred_skills)

        job_skill_set = required.union(preferred)
        if not job_skill_set:
            skills_similarity = 0.0
        else:
            intersection = applicant_skills.intersection(job_skill_set)
            union = applicant_skills.union(job_skill_set)
            skills_similarity = (len(intersection) / max(1, len(union)))

        matched_required = applicant_skills.intersection(required)
        missing_required = required.difference(applicant_skills)
        if required:
            required_coverage = len(matched_required) / len(required)
        else:
            required_coverage = 0.0

        skills_score = skills_similarity * 70.0
        skills_score += required_coverage * 20.0
        skills_score -= min(30.0, len(missing_required) * 7.5)

        location_score = 0.0
        try:
            if profile.has_coordinates() and job.has_coordinates():
                ap_lat, ap_lng = profile.get_coordinates()
                job_lat, job_lng = job.get_coordinates()
                dist_km = haversine_km(ap_lat, ap_lng, job_lat, job_lng)
                location_score = max(0.0, (50.0 - min(dist_km, 50.0)) / 50.0) * 10.0
            else:
                if profile.country and job.country and profile.country.lower() == job.country.lower():
                    location_score += 3.0
                if profile.city and job.city and profile.city.lower() == job.city.lower():
                    location_score += 5.0
        except Exception:
            location_score = 0.0

        exp_score = 0.0
        if job.experience_level == 'entry':
            exp_score = 5.0
        elif job.experience_level == 'mid':
            exp_score = 7.0
        elif job.experience_level == 'senior':
            exp_score = 4.0

        recency_boost = 0.0
        if hasattr(job, 'created_at') and job.created_at:
            days = (now - job.created_at).days
            if days <= new_job_boost_days:
                recency_boost = max(0.0, (new_job_boost_days - days) / new_job_boost_days) * 5.0

        raw = skills_score + location_score + exp_score + recency_boost
        match_score = max(0.0, min(100.0, raw))

        if match_score < 12:
            continue

        matched_skills_list = list(applicant_skills.intersection(job_skill_set))
        missing_skills_list = list(missing_required)

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

    return {'created': created, 'updated': updated, 'skipped': 0}


def generate_recommendations_for_all():
    """Generate recommendations for all active users. Returns aggregate counts."""
    from django.contrib.auth.models import User

    created = 0
    updated = 0
    skipped = 0

    users = User.objects.filter(is_active=True)
    for user in users:
        res = generate_recommendations_for_user(user)
        created += res.get('created', 0)
        updated += res.get('updated', 0)
        skipped += res.get('skipped', 0)

    return {'created': created, 'updated': updated, 'skipped': skipped}

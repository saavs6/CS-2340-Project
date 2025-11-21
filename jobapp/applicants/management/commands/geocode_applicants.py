from django.core.management.base import BaseCommand
from applicants.models import ApplicantProfile
from jobs.utils import geocode_address

class Command(BaseCommand):
    help = 'Geocode all applicant profiles that are missing coordinates'

    def handle(self, *args, **options):
        # Get all applicants without coordinates but with location data
        applicants = ApplicantProfile.objects.filter(
            latitude__isnull=True
        ) | ApplicantProfile.objects.filter(
            longitude__isnull=True
        )
        
        # Remove duplicates
        applicants = applicants.distinct()
        
        # Filter to only those with location data
        applicants = [
            app for app in applicants 
            if app.city or app.state or app.country
        ]
        
        self.stdout.write(f'Found {len(applicants)} applicants to geocode')
        
        geocoded = 0
        failed = 0
        
        for applicant in applicants:
            try:
                lat, lng = geocode_address(
                    address=None,
                    city=applicant.city,
                    state=applicant.state,
                    country=applicant.country,
                    postal_code=applicant.postal_code
                )
                
                if lat and lng:
                    applicant.latitude = lat
                    applicant.longitude = lng
                    applicant.save()
                    geocoded += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Geocoded {applicant.user.username}: {lat}, {lng}'
                        )
                    )
                else:
                    failed += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f'✗ Failed to geocode {applicant.user.username} '
                            f'({applicant.get_full_location() or "no location"})'
                        )
                    )
            except Exception as e:
                failed += 1
                self.stdout.write(
                    self.style.ERROR(
                        f'✗ Error geocoding {applicant.user.username}: {str(e)}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nCompleted: {geocoded} geocoded, {failed} failed'
            )
        )


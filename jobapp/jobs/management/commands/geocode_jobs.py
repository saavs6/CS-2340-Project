from django.core.management.base import BaseCommand
from jobs.models import Job
from jobs.utils import geocode_address

class Command(BaseCommand):
    help = 'Geocode existing jobs that don\'t have coordinates'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be geocoded without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        # Find jobs without coordinates
        jobs_without_coords = Job.objects.filter(
            latitude__isnull=True,
            longitude__isnull=True
        )

        total_jobs = jobs_without_coords.count()

        if total_jobs == 0:
            self.stdout.write(
                self.style.SUCCESS('All jobs already have coordinates!')
            )
            return

        self.stdout.write(f'Found {total_jobs} jobs without coordinates')

        if dry_run:
            self.stdout.write('DRY RUN - No changes will be made')
            for job in jobs_without_coords[:10]:  # Show first 10
                self.stdout.write(f'  - {job.title} at {job.company} ({job.get_location_display()})')
            if total_jobs > 10:
                self.stdout.write(f'  ... and {total_jobs - 10} more')
            return

        # Geocode jobs
        success_count = 0
        error_count = 0

        for job in jobs_without_coords:
            try:
                lat, lng = geocode_address(
                    address=job.full_address,
                    city=job.city,
                    state=job.state,
                    country=job.country,
                    postal_code=job.postal_code
                )

                if lat and lng:
                    job.latitude = lat
                    job.longitude = lng
                    job.save()
                    success_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Geocoded: {job.title} at {job.company}')
                    )
                else:
                    error_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'✗ Failed to geocode: {job.title} at {job.company}')
                    )

            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'✗ Error geocoding {job.title}: {str(e)}')
                )

        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(f'Geocoding complete!')
        self.stdout.write(f'Successfully geocoded: {success_count} jobs')
        self.stdout.write(f'Failed to geocode: {error_count} jobs')

        if error_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    'Some jobs failed to geocode. This might be due to:\n'
                    '- Invalid or incomplete addresses\n'
                    '- Google Maps API key issues\n'
                    '- Network connectivity problems'
                )
            )

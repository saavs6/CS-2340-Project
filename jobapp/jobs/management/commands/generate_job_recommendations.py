from django.core.management.base import BaseCommand
from jobs.recommendations import generate_recommendations_for_all


class Command(BaseCommand):
    help = 'Generate job recommendations for applicants (bulk)'

    def handle(self, *args, **options):
        res = generate_recommendations_for_all()
        self.stdout.write(self.style.SUCCESS(f"Recommendations created: {res['created']}, updated: {res['updated']}, skipped users: {res['skipped']}"))

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from applicants.models import ApplicantProfile, Education, WorkExperience
from accounts.models import UserProfile
from datetime import date, timedelta
import random

class Command(BaseCommand):
    help = 'Create test candidate data for testing the search functionality'

    def handle(self, *args, **options):
        # Create test users and profiles
        test_candidates = [
            {
                'username': 'john_developer',
                'first_name': 'John',
                'last_name': 'Smith',
                'email': 'john@example.com',
                'headline': 'Senior Python Developer with 5 years experience',
                'summary': 'Experienced Python developer specializing in Django, Flask, and data science. Passionate about building scalable web applications and machine learning solutions.',
                'skills': 'Python, Django, Flask, PostgreSQL, React, JavaScript, Machine Learning, Git',
                'city': 'San Francisco',
                'state': 'CA',
                'country': 'United States',
                'is_public': True,
                'is_seeking_jobs': True,
                'remote_work_preference': 'hybrid',
                'willing_to_relocate': True,
            },
            {
                'username': 'sarah_designer',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'email': 'sarah@example.com',
                'headline': 'UI/UX Designer and Frontend Developer',
                'summary': 'Creative designer with strong frontend development skills. Expert in user experience design, responsive web design, and modern JavaScript frameworks.',
                'skills': 'UI/UX Design, Figma, Adobe Creative Suite, React, Vue.js, CSS, HTML, JavaScript, TypeScript',
                'city': 'New York',
                'state': 'NY',
                'country': 'United States',
                'is_public': True,
                'is_seeking_jobs': True,
                'remote_work_preference': 'remote_only',
                'willing_to_relocate': False,
            },
            {
                'username': 'mike_engineer',
                'first_name': 'Mike',
                'last_name': 'Wilson',
                'email': 'mike@example.com',
                'headline': 'Full Stack Software Engineer',
                'summary': 'Versatile full-stack developer with expertise in both frontend and backend technologies. Strong problem-solving skills and experience with cloud platforms.',
                'skills': 'Java, Spring Boot, React, Node.js, AWS, Docker, Kubernetes, SQL, MongoDB',
                'city': 'Austin',
                'state': 'TX',
                'country': 'United States',
                'is_public': True,
                'is_seeking_jobs': True,
                'remote_work_preference': 'flexible',
                'willing_to_relocate': True,
            },
            {
                'username': 'lisa_data',
                'first_name': 'Lisa',
                'last_name': 'Brown',
                'email': 'lisa@example.com',
                'headline': 'Data Scientist and Analytics Expert',
                'summary': 'Data scientist with strong background in statistics, machine learning, and business intelligence. Experience with big data technologies and visualization.',
                'skills': 'Python, R, SQL, Machine Learning, TensorFlow, PyTorch, Tableau, Power BI, Apache Spark',
                'city': 'Seattle',
                'state': 'WA',
                'country': 'United States',
                'is_public': True,
                'is_seeking_jobs': False,  # Not currently seeking
                'remote_work_preference': 'hybrid',
                'willing_to_relocate': False,
            },
            {
                'username': 'david_devops',
                'first_name': 'David',
                'last_name': 'Lee',
                'email': 'david@example.com',
                'headline': 'DevOps Engineer and Cloud Architect',
                'summary': 'DevOps engineer specializing in cloud infrastructure, automation, and CI/CD pipelines. Strong experience with containerization and monitoring.',
                'skills': 'AWS, Azure, Docker, Kubernetes, Terraform, Jenkins, GitLab CI, Python, Bash, Linux',
                'city': 'Denver',
                'state': 'CO',
                'country': 'United States',
                'is_public': False,  # Private profile
                'is_seeking_jobs': True,
                'remote_work_preference': 'remote_only',
                'willing_to_relocate': True,
            }
        ]

        created_count = 0
        for candidate_data in test_candidates:
            # Create or get user
            user, created = User.objects.get_or_create(
                username=candidate_data['username'],
                defaults={
                    'first_name': candidate_data['first_name'],
                    'last_name': candidate_data['last_name'],
                    'email': candidate_data['email'],
                }
            )
            
            if created:
                user.set_password('testpass123')
                user.save()
                
                # Create user profile
                UserProfile.objects.create(
                    user=user,
                    user_type='applicant'
                )
                
                # Create applicant profile
                profile = ApplicantProfile.objects.create(
                    user=user,
                    headline=candidate_data['headline'],
                    summary=candidate_data['summary'],
                    skills=candidate_data['skills'],
                    city=candidate_data['city'],
                    state=candidate_data['state'],
                    country=candidate_data['country'],
                    is_public=candidate_data['is_public'],
                    is_seeking_jobs=candidate_data['is_seeking_jobs'],
                    remote_work_preference=candidate_data['remote_work_preference'],
                    willing_to_relocate=candidate_data['willing_to_relocate'],
                )
                
                # Add some education
                Education.objects.create(
                    applicant=profile,
                    institution='University of California',
                    degree="Bachelor's Degree",
                    field_of_study='Computer Science',
                    start_date=date(2015, 9, 1),
                    end_date=date(2019, 6, 1),
                    gpa=3.7
                )
                
                # Add some work experience
                WorkExperience.objects.create(
                    applicant=profile,
                    company='Tech Company Inc.',
                    position='Software Developer',
                    start_date=date(2019, 7, 1),
                    end_date=date(2022, 12, 31),
                    location=candidate_data['city'] + ', ' + candidate_data['state'],
                    description='Developed and maintained web applications using modern technologies. Collaborated with cross-functional teams to deliver high-quality software solutions.'
                )
                
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created candidate: {user.get_full_name()}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} test candidates')
        )

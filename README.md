# CS 2340B: Team #18

## Project Description

Early-career job seekers often face challenges finding roles that match their skills, interests, and location preferences. At the same time, recruiters struggle to identify and evaluate applicants who are a good fit for their openings, especially when managing large pools of candidates.

Our team has been asked to design and build a web application that bridges this gap. The platform should serve as a meeting point between young professionals searching for opportunities and recruiters looking for talent. It should support creating and managing professional profiles, posting and exploring job opportunities, and enabling recruiters to search, track, and engage with applicants.

Because location plays a key role in employment, the platform should also integrate map-based features to help job seekers visualize opportunities geographically and recruiters understand applicant distribution.

This project is intended to challenge us to think about multiple perspectives (considering Job Seekers, Recruiters, and Administrators) while practicing core software engineering skills such as requirements analysis, system design, team collaboration, and web development.

## Prerequisites

Before running this application, ensure you have Python 3.8 or higher, pip (Python package installer), and Git for cloning the repository.

## Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/saavs6/CS-2340-Project.git
cd CS-2340-Project
```

### 2. Navigate to the Django Project
```bash
cd jobapp
```

### 3. Create a Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install django
```

### 5. Run Database Migrations
```bash
python manage.py migrate
```

### 6. Create a Superuser (Optional)
```bash
python manage.py createsuperuser
```

### 7. Start the Development Server
```bash
python manage.py runserver
```

### 8. Access the Application
Open your web browser and navigate to:
- **Main Application**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/

## Project Structure

```
jobapp/
├── accounts/           # User authentication and profiles
├── applicants/         # Job seeker functionality
├── recruiters/         # Recruiter functionality
├── home/              # Landing page and general views
├── jobapp/            # Main Django project settings
│   ├── static/        # CSS, images, and static files
│   └── templates/     # Base templates
├── manage.py          # Django management script
└── db.sqlite3         # SQLite database (created after migration)
```

## User Stories

### Job Seeker
1.  As a Job Seeker, I want to create a profile with my headline, skills, education, work experience, and links so recruiters can learn about me.
2.  As a Job Seeker, I want to search for jobs with filters (title, skills, location, salary range, remote/on-site, visa sponsorship) so I can find opportunities that match my needs.
3.  As a Job Seeker, I want to apply to a job with one click and include a tailored note so my application feels personalized.
4.  As a Job Seeker, I want to track the status of my applications (Applied → Review → Interview → Offer → Closed) so I know where I stand.
5.  As a Job Seeker, I want to set privacy options on my profile so I control what recruiters can see.
6.  As a Job Seeker, I want to receive recommendations for jobs based on my skills so I discover opportunities I might have missed.
7.  As a Job Seeker, I want to view job postings on an interactive map so I can see which ones are near me.
8.  As a Job Seeker, I want to filter jobs on the map by distance from my current location so I can prioritize nearby opportunities.
9.  As a Job Seeker, I want to set a preferred commute radius (e.g., 10 miles) on the map so I only see jobs within a reasonable travel distance.

### Recruiter
10. As a Recruiter, I want to post and edit job roles so candidates can apply to my openings.
11. As a Recruiter, I want to search for candidates by skills, location, and projects so I can find talent that fits my positions.
12. As a Recruiter, I want to organize applicants in a pipeline (e.g., a Kanban board) so I can easily manage hiring stages.
13. As a Recruiter, I want to message candidates inside the platform so I can contact them without the use of personal emails.
14. As a Recruiter, I want to email candidate through the platform so I can reach out to them through their personal emails.
15. As a Recruiter, I want to save a candidate search and get notified about new matches so I don't have to repeat the same queries.
16. As a Recruiter, I want to receive candidate recommendations for my job postings so I find qualified applicants faster.
17. As a Recruiter, I want to pin my job posting's office location on a map so candidates know exactly where the job is based.
18. As a Recruiter, I want to see clusters of applicants by location on a map so I understand where most candidates are coming from.

### Administrator
19. As an Administrator, I want to manage users and roles so the platform remains fair and safe.
20. As an Administrator, I want to moderate or remove job posts so the platform stays free of spam or abuse.
21. As an Administrator, I want to export data (CSV) for reporting purposes so stakeholders can analyze usage.

## Team Information

### Team Members & Roles
* **Scrum Master:** Johnny C
* **Product Owner/PM:** Sean S
* **Developers:** Wiley G, Sam C, Hanzhang L

### Development Responsibilities
* **Frontend:** Johnny C, Wiley G
* **Backend:** Sean S, Sam C
* **Full Stack:** Hanzhang L

## Project Management & Communication

### Meetings
* **TA Meetings:** Fridays from 3:30 - 4:00 PM. A second meeting time is to be determined.


### Tools
* **Scheduling:** [LettuceMeet](https://lettucemeet.com/l/5l7lY)
* **Task Management:** [Trello Board](https://trello.com/invite/b/68c090410661ff2552b4116a/ATTIfad5a0ba0d2959998fd41048a5089df3B9C5C844/2340b-team-18)

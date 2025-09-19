from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def index(request):
    template_data = {}
    template_data['title'] = 'LinkedOut - Your Ticket to Unlimited Jobs!'

    # Check if user is logged in and has a profile
    if request.user.is_authenticated:
        try:
            profile = request.user.userprofile
            template_data['user_type'] = profile.user_type
            template_data['is_applicant'] = profile.user_type == 'applicant'
            template_data['is_recruiter'] = profile.user_type == 'recruiter'
        except:
            template_data['user_type'] = None
            template_data['is_applicant'] = False
            template_data['is_recruiter'] = False
    else:
        template_data['user_type'] = None
        template_data['is_applicant'] = False
        template_data['is_recruiter'] = False

    return render(request, 'home/index.html', {
        'template_data': template_data})
def about(request):
    template_data = {}
    template_data['title'] = 'About'
    return render(request,
                  'home/about.html',
                  {'template_data': template_data})
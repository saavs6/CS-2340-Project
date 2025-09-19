from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404

def user_type_required(user_type):
    """
    Decorator that requires a user to be logged in and have a specific user type.

    Usage:
    @user_type_required('applicant')
    def applicant_dashboard(request):
        # This view is only accessible to applicants
        pass
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            try:
                profile = request.user.userprofile
                if profile.user_type != user_type:
                    # Redirect to appropriate dashboard based on user type
                    if profile.user_type == 'applicant':
                        return redirect('applicants:dashboard')
                    elif profile.user_type == 'recruiter':
                        return redirect('recruiters:dashboard')
                    else:
                        return redirect('home.index')
                return view_func(request, *args, **kwargs)
            except:
                # If user doesn't have a profile, redirect to home
                return redirect('home.index')
        return wrapper
    return decorator

def applicant_required(view_func):
    """Shortcut decorator for applicant-only views"""
    return user_type_required('applicant')(view_func)

def recruiter_required(view_func):
    """Shortcut decorator for recruiter-only views"""
    return user_type_required('recruiter')(view_func)

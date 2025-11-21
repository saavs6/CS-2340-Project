from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from functools import wraps

def admin_required(view_func):
    """
    Decorator to check if user is an admin.
    Admin is defined as: user with is_staff=True, is_superuser=True, or user_type='admin'
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return redirect('accounts.login')

        # Check if user is staff or superuser
        if request.user.is_staff or request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        # Check if user has admin user_type in their profile
        try:
            if hasattr(request.user, 'userprofile') and request.user.userprofile.user_type == 'admin':
                return view_func(request, *args, **kwargs)
        except:
            pass

        # If none of the above, deny access
        return HttpResponseForbidden("You do not have permission to access this page.")

    return wrapper

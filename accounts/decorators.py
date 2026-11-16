from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def role_required(role):
    """Allow only logged-in users with the given role.

    Logged-out users go to the login page (via @login_required).
    Logged-in users with a different role are sent back to their own dashboard,
    so typing another role's URL never shows that page.
    """

    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.role != role:
                messages.error(request, 'You do not have permission to open that page.')
                return redirect('accounts:dashboard')
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator

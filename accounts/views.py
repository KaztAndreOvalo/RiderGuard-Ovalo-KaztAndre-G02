from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .decorators import role_required
from .forms import LoginForm, ProfileForm, RegistrationForm

User = get_user_model()


def home(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    return render(request, 'accounts/home.html')


def register(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created! You can now log in.')
            return redirect('accounts:login')
        messages.error(request, 'Please fix the errors below.')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


class RiderGuardLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, f'Welcome back, {form.get_user().first_name or form.get_user().username}!')
        return super().form_valid(form)


@require_POST
def logout_view(request):
    logout(request)  # Flushes the session.
    messages.success(request, 'You have been logged out.')
    return redirect('accounts:login')


@login_required
def dashboard(request):
    """Send each user to the dashboard for their role."""
    if request.user.is_admin_role:
        return redirect('accounts:admin_dashboard')
    return redirect('accounts:rider_dashboard')


@role_required(User.Role.RIDER)
def rider_dashboard(request):
    # Trip Logger, Fare Checker and Dispute Vault arrive in later sprints;
    # the summary cards show zeros until those modules exist.
    context = {
        'earnings_today': 0,
        'earnings_week': 0,
        'flagged_fares': 0,
        'pending_disputes': 0,
    }
    return render(request, 'accounts/rider_dashboard.html', context)


@role_required(User.Role.ADMIN)
def admin_dashboard(request):
    riders = User.objects.filter(role=User.Role.RIDER)
    context = {
        'total_riders': riders.count(),
        'active_riders': riders.filter(is_active=True).count(),
        'total_admins': User.objects.filter(role=User.Role.ADMIN).count(),
        'recent_riders': riders.order_by('-date_joined')[:8],
    }
    return render(request, 'accounts/admin_dashboard.html', context)


@login_required
def profile(request):
    # Always the logged-in user's own profile; there is no user id in the URL.
    return render(request, 'accounts/profile.html', {'profile_user': request.user})


@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated.')
            return redirect('accounts:profile')
        messages.error(request, 'Please fix the errors below.')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'accounts/profile_edit.html', {'form': form})

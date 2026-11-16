from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class UsernameOrEmailBackend(ModelBackend):
    """Let users sign in with either their username or their email address."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
        User = get_user_model()
        lookup = 'email__iexact' if '@' in username else 'username__iexact'
        try:
            user = User.objects.get(**{lookup: username})
        except User.DoesNotExist:
            # Run the hasher anyway so timing doesn't reveal which accounts exist.
            User().set_password(password)
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

from django.contrib.auth.models import AbstractUser, UserManager
from django.core.validators import RegexValidator
from django.db import models


class RiderGuardUserManager(UserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        # Anyone created with `createsuperuser` is a RiderGuard admin.
        extra_fields.setdefault('role', User.Role.ADMIN)
        return super().create_superuser(username, email, password, **extra_fields)


class User(AbstractUser):
    class Role(models.TextChoices):
        RIDER = 'RIDER', 'Rider'
        ADMIN = 'ADMIN', 'Admin'

    PLATFORM_CHOICES = [
        ('MAXIM', 'Maxim'),
        ('MOVEIT', 'MoveIt'),
        ('GRAB', 'Grab'),
        ('ANGKAS', 'Angkas'),
        ('JOYRIDE', 'JoyRide'),
        ('LALAMOVE', 'Lalamove'),
        ('FOODPANDA', 'foodpanda'),
        ('OTHER', 'Other'),
    ]

    phone_validator = RegexValidator(
        regex=r'^(09\d{9}|\+639\d{9})$',
        message='Enter a valid PH mobile number, e.g. 09171234567 or +639171234567.',
    )

    email = models.EmailField('email address', unique=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.RIDER)
    contact_number = models.CharField(max_length=13, blank=True, validators=[phone_validator])
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    platforms = models.CharField(
        max_length=200, blank=True,
        help_text='Comma-separated platform codes the rider works for.',
    )
    vehicle_type = models.CharField(max_length=50, blank=True)
    plate_number = models.CharField(max_length=15, blank=True)

    objects = RiderGuardUserManager()

    @property
    def is_rider(self):
        return self.role == self.Role.RIDER

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN

    @property
    def platform_list(self):
        return [p for p in self.platforms.split(',') if p]

    @property
    def platform_labels(self):
        labels = dict(self.PLATFORM_CHOICES)
        return [labels.get(p, p) for p in self.platform_list]

    def __str__(self):
        return self.username

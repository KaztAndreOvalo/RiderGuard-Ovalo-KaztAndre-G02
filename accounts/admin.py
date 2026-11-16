from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class RiderGuardUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active')
    list_filter = ('role', 'is_active', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('RiderGuard', {
            'fields': ('role', 'contact_number', 'profile_photo', 'platforms', 'vehicle_type', 'plate_number'),
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('RiderGuard', {'fields': ('email', 'role')}),
    )

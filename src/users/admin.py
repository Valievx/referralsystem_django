from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from users.models import User


class CustomUserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('phone_number', 'confirmation_code')}),
        ('Personal info', {'fields': ('inviter_code',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    ordering = ('phone_number',)
    list_display = (
        'pk',
        'phone_number',
        'confirmation_code',
        'my_invite_code',
        'inviter_code')


admin.site.register(User, CustomUserAdmin)

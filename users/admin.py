from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    # Fields to display in admin list view
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')

    # Fields to use for searching
    search_fields = ('email', 'first_name', 'last_name')

    # Fieldsets: organize fields in the edit page
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', )}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

    # Fields for creating a new user via admin
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )

    ordering = ('email',)  # Order by email
    

admin.site.register(CustomUser, CustomUserAdmin)

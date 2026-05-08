# home/admin.py
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Division, District, Upazila, Union, Ward, House



admin.site.register(Division)
admin.site.register(District)
admin.site.register(Upazila)
admin.site.register(Union)
admin.site.register(Ward)
admin.site.register(House)

CustomUser = get_user_model()

@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ('email', 'name', 'user_type', 'is_active', 'is_staff')
    list_filter = ('user_type', 'is_active')
    search_fields = ('email', 'name')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name', 'user_type', 'division', 'district', 'upazila', 'union', 'ward')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Groups and Permissions', {'fields': ('groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    def get_fieldsets(self, request, obj=None):
        """
        Dynamically adjust fieldsets based on the user's user_type.
        """
        fieldsets = super().get_fieldsets(request, obj)
        if obj:  # When editing an existing user
            user_type = obj.user_type
            if user_type == 'Admin' or user_type == 'Public':
                # Remove place fields for Admin/Public
                fieldsets[1][1]['fields'] = ('name', 'user_type')
        return fieldsets

    def save_model(self, request, obj, form, change):
        """
        Call clean before saving to enforce the constraints.
        """
        obj.clean()
        super().save_model(request, obj, form, change)

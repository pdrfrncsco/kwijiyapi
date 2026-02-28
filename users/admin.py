from django.contrib import admin
from .models import CustomUser, OTPCode


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['email', 'username', 'level', 'total_xp', 'streak_days', 'is_guest', 'created_at']
    list_filter = ['age_group', 'is_guest', 'is_active']
    search_fields = ['email', 'username']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    list_display = ['email', 'code', 'is_used', 'created_at', 'expires_at']
    list_filter = ['is_used']
    search_fields = ['email']

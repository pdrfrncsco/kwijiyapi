from django.contrib import admin
from .models import UserXPLog, Badge, UserBadge


@admin.register(UserXPLog)
class UserXPLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'xp_gained', 'source', 'created_at']
    list_filter = ['source']


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'xp_required']


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ['user', 'badge', 'awarded_at']

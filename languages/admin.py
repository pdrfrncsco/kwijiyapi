from django.contrib import admin
from .models import Language


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'region', 'difficulty_level', 'is_active']
    list_filter = ['difficulty_level', 'is_active']
    search_fields = ['name', 'code']

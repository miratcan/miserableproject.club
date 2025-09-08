from django.contrib import admin
from .models import Submission


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('project_name', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('project_name', 'tagline')
    actions = ['mark_published', 'mark_removed', 'mark_flagged']

    @admin.action(description='Mark selected as published')
    def mark_published(self, request, queryset):
        queryset.update(status='published')

    @admin.action(description='Mark selected as removed')
    def mark_removed(self, request, queryset):
        queryset.update(status='removed')

    @admin.action(description='Mark selected as flagged')
    def mark_flagged(self, request, queryset):
        queryset.update(status='flagged')


# Report removed for MVP

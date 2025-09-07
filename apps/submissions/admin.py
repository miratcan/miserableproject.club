from django.contrib import admin
from .models import Submission, Report


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'snapshot')
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


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'target_type', 'target_id', 'status', 'created_at')
    list_filter = ('status', 'target_type', 'created_at')
    search_fields = ('reason',)
    actions = ['close_reports']

    @admin.action(description='Close selected reports')
    def close_reports(self, request, queryset):
        queryset.update(status='closed')


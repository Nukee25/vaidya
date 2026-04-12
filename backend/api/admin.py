from django.contrib import admin

from .models import DiagnosisReport


@admin.register(DiagnosisReport)
class DiagnosisReportAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "diagnosis", "severity", "status", "created_at")
    search_fields = ("user__username", "diagnosis", "summary")
    list_filter = ("severity", "status", "created_at")
    date_hierarchy = "created_at"

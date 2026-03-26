from django.contrib import admin

from .models import DiagnosisReport


@admin.register(DiagnosisReport)
class DiagnosisReportAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "diagnosis", "severity", "status", "created_at")
    search_fields = ("user__username", "diagnosis", "summary")

# Register your models here.

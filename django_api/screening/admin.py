from django.contrib import admin
from .models import Applicant, Screening, Feedback


@admin.register(Applicant)
class ApplicantAdmin(admin.ModelAdmin):
    list_display = ("applicant_id", "name", "age", "employment_type", "monthly_income")
    search_fields = ("applicant_id", "name")


@admin.register(Screening)
class ScreeningAdmin(admin.ModelAdmin):
    list_display = ("job_id", "status", "created_at")
    list_filter = ("status",)


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("screening", "correct", "created_at")
    list_filter = ("correct",)

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"applicants", views.ApplicantViewSet, basename="applicant")
router.register(r"screenings", views.ScreeningViewSet, basename="screening")

urlpatterns = [
    path("screen/", views.screen_applicant_view, name="screen"),
    path("screen/<str:job_id>/status/", views.screen_status_view, name="screen-status"),
    path("feedback/", views.feedback_view, name="feedback"),
    path("screenings/<int:screening_id>/review/", views.review_screening, name="screen-review"),
    path("dashboard/summary/", views.dashboard_view, name="dashboard-summary"),
    path("", include(router.urls)),
]

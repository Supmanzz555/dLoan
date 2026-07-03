from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register, name="auth-register"),
    path("login/", views.login, name="auth-login"),
    path("refresh/", views.refresh_view, name="auth-refresh"),
    path("logout/", views.logout_view, name="auth-logout"),
    path("change-password/", views.change_password, name="auth-change-password"),
    path("profile/", views.profile, name="auth-profile"),
    path("users/", views.user_list, name="auth-user-list"),
    path("users/<int:user_id>/", views.user_detail, name="auth-user-detail"),
    path("activity/", views.activity_log_view, name="auth-activity"),
]

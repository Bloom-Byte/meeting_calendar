from django.urls import path

from . import views

app_name = "users"


urlpatterns = [
    # Account creation and authentication
    path("signup/", views.user_create_view, name="signup"),
    path("signin/", views.user_login_view, name="signin"),
    path("signout/", views.user_logout_view, name="signout"),
    path("forgot-password/", views.forgot_password_view, name="forgot_password"),
    path("reset-password/", views.user_password_reset_view, name="reset_password"),

    # Account detail and management
    path("<str:slug>/", views.user_account_view, name="account_detail"),
    path("<str:slug>/change-password/", views.user_account_password_change_view, name="password_change"),
    path("<str:slug>/update/", views.user_account_update_view, name="account_update"),
    path("<str:slug>/delete/", views.user_account_delete_view, name="account_delete"),
]

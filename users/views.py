import json
from typing import Any, Dict
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views import generic
from django.conf import settings
import functools
from urllib.parse import urlencode as urllib_urlencode
import pytz


from .forms import UserCreationForm, UserUpdateForm
from .models import UserAccount
from .decorators import redirect_authenticated, email_request_user_on_response
from .utils import parse_query_params_from_request, get_password_change_mail_body
from .password_reset import (
    check_if_password_reset_token_exists, create_password_reset_token,
    delete_password_reset_token, construct_password_reset_mail,
    check_password_reset_token_validity, reset_password_for_token
)
from helpers.logging import log_exception



class UserCreateView(generic.CreateView):
    """View for creating a user."""
    form_class = UserCreationForm
    template_name = "users/signup.html"

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> JsonResponse:
        """Handles user creation AJAX/Fetch POST request"""
        data: Dict = json.loads(request.body)
        form = self.get_form_class()(data)

        if form.is_valid():
            user: UserAccount = form.save(commit=False)
            user.save()
            return JsonResponse(
                data={
                    "status": "success",
                    "detail": "Account created successfully!",
                    "redirect_url": reverse("users:signin")
                },
                status=201
            )

        return JsonResponse(
            data={
                "status": "error",
                "detail": "An error occurred while creating account!",
                "errors": form.errors,
            },
            status=400
        )



class UserLoginView(generic.TemplateView):
    """View for authenticating a user."""
    template_name = "users/signin.html"

    @redirect_authenticated("dashboard:dashboard")
    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        return super().get(request, *args, **kwargs)


    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> JsonResponse:
        """Handles user authentication AJAX/Fetch POST request"""
        data: Dict = json.loads(request.body)
        email = data.get('email', None)
        password = data.get('password', None)
        current_timezone = data.get('timezone', None)
        
        user = authenticate(request, username=email, password=password)
        if user:
            if current_timezone:
                user.timezone = current_timezone
                user.save()
            login(request, user)
            
            query_params = parse_query_params_from_request(request)
            next_url = query_params.pop("next", None) 
            if next_url and query_params:
                other_query_params = urllib_urlencode(query_params)
                next_url = f"{next_url}?{other_query_params}"
            return JsonResponse(
                data={
                    "status": "success",
                    "detail": f"Welcome {user.fullname}!",
                    "redirect_url": next_url or reverse("dashboard:dashboard")
                },
                status=200
            )
        
        return JsonResponse(
            data={
                "status": "error",
                "detail": "Incorrect email or password!"
            },
            status=400
        )
 

class UserLogoutView(generic.RedirectView):
    """View for logging out a user."""
    url = "/accounts/signin/"

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> None:
        if request.user.is_authenticated:
            logout(request)
        return super().get(request, *args, **kwargs)



class ForgotPasswordView(generic.TemplateView):
    """View for handling forgot password requests."""
    template_name = "users/forgot_password.html"
    http_method_names = ["get", "post"]

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> JsonResponse:
        data: Dict = json.loads(request.body)
        email: str = data.get("email", None)
        token = None

        try:
            user = UserAccount.objects.get(email=email)
        except UserAccount.DoesNotExist:
            return JsonResponse(
                data={
                    "status": "error",
                    "detail": f"User account with email address {email}, not found!"
                },
                status=404
            )
        
        if check_if_password_reset_token_exists(user) is True:
            # If a token already exists, then the user has already requested a password reset
            # and should wait for the email to be sent to them or check their email for the link.
            return JsonResponse(
                data={
                    "status": "error",
                    "detail": f"A password reset request was recently made for this account! Please check {user.email} for a reset email!"
                },
                status=400
            )
        
        try:
            # Create a token that is only valid for 24 hours
            validity_period = settings.PASSWORD_RESET_TOKEN_VALIDITY_PERIOD
            token = create_password_reset_token(user, validity_period_in_hours=validity_period)
            reset_url = f"{settings.SITE_URL}{reverse('users:reset_password')}"
            message = construct_password_reset_mail(
                user=user, 
                password_reset_url=reset_url, 
                token=token,
                token_name="token",
                token_validity_period=validity_period
            )
            user.send_mail("Account Password Reset", message, html=True)
        except Exception as exc:
            log_exception(exc)
            if token:
                # Delete the created token if an error occurs
                delete_password_reset_token(token)
            return JsonResponse(
                data={
                    "status": "error",
                    "detail": "An error occurred while processing your request. Please try again."
                },
                status=500
            )
        
        return JsonResponse(
            data={
                "status": "success",
                "detail": f"Request processed successfully. An email has been sent to {user.email}.",
                "redirect_url": reverse("users:signin")
            },
            status=200
        )



class UserAccountPasswordResetView(generic.TemplateView):
    """View for resetting user account password"""
    http_method_names = ["get", "post"]
    template_name = "users/reset_password.html"
    
    def post(self, request, *args, **kwargs) -> JsonResponse:
        data: Dict = json.loads(request.body)
        new_password = data.get("new-password1")
        query_params = parse_query_params_from_request(request)
        token = query_params.get("token", None)
        token_is_valid = check_password_reset_token_validity(token)
        reset_successful = False
        
        if token_is_valid is False:
            # Delete the token so the user can request a password rest again
            delete_password_reset_token(token)
            return JsonResponse(
                data={
                    "status": "error",
                    "detail": "The password reset token is invalid or has expired! Please request a password reset again.",
                },
                status=400
            )
        
        try:
            reset_successful = reset_password_for_token(token, new_password)
        except Exception as exc:
            log_exception(exc)
            return JsonResponse(
                data={
                    "status": "error",
                    "detail": "An error occurred while attempting password reset!"
                },
                status=500
            )
        
        if not reset_successful:
            return JsonResponse(
                data={
                    "status": "error",
                    "detail": "Password reset was unsuccessful! Please try again."
                },
                status=400
            )
        
        return JsonResponse(
            data={
                "status": "success",
                "detail": "Password reset was successful!",
                "redirect_url": reverse("users:signin")
            },
            status=200
        )



class UserAccountDetailView(LoginRequiredMixin, generic.DetailView):
    """View for getting a user's account details."""
    model = UserAccount
    template_name = "users/user_account.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"
    context_object_name = "user"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["timezones"] = pytz.all_timezones
        return context
    


class UserAccountPasswordChangeView(LoginRequiredMixin, generic.DetailView):
    """View for changing a user's password."""
    model = UserAccount
    http_method_names = ["post"]
    slug_field = "slug"
    slug_url_kwarg = "slug"

    email_request_user_on_password_change = functools.partial(
        email_request_user_on_response, 
        subject="Account Password Changed", 
        body=get_password_change_mail_body()
    )

    @email_request_user_on_password_change
    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> JsonResponse:
        """Handles user password change AJAX/Fetch POST request"""
        data: Dict = json.loads(request.body)
        user: UserAccount = self.get_object()
        current_password = data.get("old-password", None)
        new_password = data.get("new-password1", None)
        confirm_password = data.get("new-password2", None)

        if not current_password:
            return JsonResponse(
                data={
                    "status": "error",
                    "detail": "Current password not provided!"
                },
                status=400
            )

        if not new_password:
            return JsonResponse(
                data={
                    "status": "error",
                    "detail": "New password not provided!"
                },
                status=400
            )
        
        if current_password == new_password:
            return JsonResponse(
                data={
                    "status": "error",
                    "detail": "New password cannot be the same as the current password!"
                },
                status=400
            )

        if new_password != confirm_password:
            return JsonResponse(
                data={
                    "status": "error",
                    "detail": "New password and confirm password do not match!"
                },
                status=400
            )

        if user.check_password(current_password):
            user.set_password(new_password)
            user.save()
            return JsonResponse(
                data={
                    "status": "success",
                    "detail": "Password changed successfully!"
                },
                status=200
            )
        
        return JsonResponse(
            data={
                "status": "error",
                "detail": "Incorrect current password!"
            },
            status=400
        )



class UserAccountUpdateView(LoginRequiredMixin, generic.UpdateView):
    """View for updating a user's account details."""
    model = UserAccount
    form_class = UserUpdateForm
    slug_field = "slug"
    slug_url_kwarg = "slug"
    context_object_name = "user"
    http_method_names = ["post"]

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> JsonResponse:
        """Handles user detail update AJAX/Fetch POST request"""
        data: Dict = json.loads(request.body)
        user = self.get_object()
        form = self.get_form_class()(data=data, instance=user)

        if form.is_valid():
            user: UserAccount = form.save(commit=False)
            user.save()
            return JsonResponse(
                data={
                    "status": "success",
                    "detail": "Account update successfully!",
                    "redirect_url": reverse("users:account_detail", kwargs={"slug": user.slug}),
                },
                status=200
            )

        return JsonResponse(
            data={
                "status": "error",
                "detail": "An error occurred while updating account!",
                "errors": form.errors,
            },
            status=400
        )


class UserAccountDeleteView(LoginRequiredMixin, generic.DetailView):
    """View for deleting a sale record from a store."""
    model = UserAccount
    http_method_names = ["get"]
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get(self, request, *args, **kwargs):
        user = self.get_object()
        user.delete()
        return redirect("users:signin")




# Account creation and authentication
user_create_view = UserCreateView.as_view()
user_login_view = UserLoginView.as_view()
user_logout_view = UserLogoutView.as_view()
forgot_password_view = ForgotPasswordView.as_view()
user_password_reset_view = UserAccountPasswordResetView.as_view()


# Account management
user_account_view = UserAccountDetailView.as_view()
user_account_password_change_view = UserAccountPasswordChangeView.as_view()
user_account_update_view = UserAccountUpdateView.as_view()
user_account_delete_view = UserAccountDeleteView.as_view()


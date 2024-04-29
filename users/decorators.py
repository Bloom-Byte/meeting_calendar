from typing import Any, Callable
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect
import functools
from django.conf import settings

from .models import UserAccount


def to_JsonResponse(func: Callable[..., HttpResponse]) -> Callable[..., JsonResponse]:
    """Ensures that the decorated view returns a JsonResponse."""
    @functools.wraps(func)
    def wrapper(request: HttpRequest, *args, **kwargs) -> JsonResponse:
        response = func(request, *args, **kwargs)

        if isinstance(response, JsonResponse):
            return response
        
        return JsonResponse(
            data={
                "status": "error" if response.status_code >= 400 else "success",
                "detail": response.content.decode(),
            }, 
            status=response.status_code
        )
    
    return wrapper



def redirect_authenticated(redirect_view: Callable | str):
    """
    Create a decorator that redirects authenticated users to a view.

    :param redirect_view: The view to redirect to. Could be a view, view name or url.
    """
    def decorator(view_func: Callable[..., HttpResponse | JsonResponse]):
        """
        Decorator that redirects authenticated users to a view.

        :param view_func: The view function to decorate.
        """
        @functools.wraps(view_func)
        def wrapper(self, request: HttpRequest, *args: str, **kwargs: Any):
            if request.user.is_authenticated:
                return redirect(redirect_view)
            return view_func(self, request, *args, **kwargs)
        return wrapper
    
    return decorator



def requires_account_verification(
        view_func: Callable[..., HttpResponse | JsonResponse] = None,
        error_msg: str = "Email verification required! Please verify your account email and try again."
    ):
    """
    Ensures a user verifies account email before accessing the view.

    :param view_func: The view function to decorate.
    :param error_msg: The error message to return if the user is not verified.
    """
    def decorator(view_func: Callable[..., HttpResponse | JsonResponse]):
        """
        Ensures a user verifies account email before accessing decorated view.
        """
        @functools.wraps(view_func)
        def wrapper(view, request: HttpRequest, *args: str, **kwargs: Any):
            if request.user.is_verified:
                return view_func(view, request, *args, **kwargs)

            return HttpResponse(content=error_msg, status=403)
        return wrapper
    
    if view_func:
        return decorator(view_func)
    return decorator



def email_request_user_on_response(
        view_func: Callable[..., HttpResponse | JsonResponse] = None,
        *,
        status_code: int = 200,
        subject: str = None,
        body: str = None 
    ) -> Callable[..., HttpResponse | JsonResponse]:
    """
    Decorator that sends an email to the user on view response.

    :param view_func: The view function to decorate.
    :param status_code: The status code of the response to send the email on.
    :param subject: The subject of the email to send.
    :param body: The body of the email to send.
    """
    def decorator(view_func: Callable[..., HttpResponse | JsonResponse]):
        """
        Decorator that sends an email to the user on view response.
        """
        @functools.wraps(view_func)
        def wrapper(view, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse | JsonResponse:
            response = view_func(view, request, *args, **kwargs)
            sub = subject
            bod = body
            if not sub:
                sub = f"Request to {request.path}"
            if not bod:
                bod = f"Your request to {settings.BASE_URL}/{request.path} got response {response.status_code} - {response.reason_phrase}"
            if response.status_code == status_code:
                user: UserAccount = request.user
                try:
                    user.send_mail(sub, bod)
                except Exception:
                    pass
                
            return response
        return wrapper
    
    if view_func:
        return decorator(view_func)
    return decorator
    

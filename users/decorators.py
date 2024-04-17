from typing import Any, Callable
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect
import functools
from django.conf import settings

from .models import UserAccount


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
    

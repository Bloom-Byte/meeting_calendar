import re
from django.http import HttpRequest
from typing import Any, Dict
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.template.loader import render_to_string

from .models import UserAccount


def parse_query_params_from_request(request: HttpRequest) -> Dict[str, str]:
    """Parses the query parameters from a request. Returns a dictionary of the query parameters."""
    if request.method != "POST":
        return request.GET.dict()
    
    query_param_pattern = r"&?(?P<param_name>[a-zA-Z0-9-_\.\s]+)=(?P<param_value>[a-zA-Z0-9-_/\.\?=\\\s]+)"
    request_path: str = request.META.get("HTTP_REFERER", "")
    try:
        _, query_params_part = request_path.split("?", maxsplit=1)
        results = re.findall(query_param_pattern, query_params_part)
        if not results:
            return {}
    except ValueError:
        return {}
    return {param_name: param_value for param_name, param_value in results}


def underscore_dict_keys(_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Replaces all hyphens in the dictionary keys with underscores"""
    return {key.replace('-', "_"): value for key, value in _dict.items()}


def get_password_change_mail_body() -> str:
    return f"""
    Your {settings.SITE_NAME} account password has been changed successfully.\n
    If you did not make this change, please contact the site administrator immediately.
    """ 


def construct_verification_email(user: UserAccount) -> str:
    """Construct the verification email body."""
    verification_link = f"{settings.SITE_URL}/{reverse('users:email_verification', kwargs={'token': user.id.hex})}"
    context = {
        "username": user.name,
        "verification_link": verification_link,
        "current_year": timezone.now().year,
        "site_name": settings.SITE_NAME,
    }
    return render_to_string("emails/verification_email.html", context=context)


def send_verification_email(user: UserAccount) -> None:
    """Send verification email to user."""
    if user.is_verified:
        return
    subject = "Verify your email address"
    body = construct_verification_email(user)
    return user.send_mail(subject, body, html=True)

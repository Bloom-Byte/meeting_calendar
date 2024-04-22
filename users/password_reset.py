from django.template.loader import render_to_string
from django.conf import settings
import datetime
from typing import Optional, Union
from django.utils import timezone

from .models import UserAccount
from tokens.models import PasswordResetToken


def check_if_password_reset_token_exists(user: UserAccount) -> bool:
    """Check if a password reset token already exists for the given user."""
    return PasswordResetToken.objects.filter(user=user).exists()


def create_password_reset_token(user: UserAccount, validity_period_in_hours: Optional[Union[int, float]] = None) -> str:
    """
    Create a password reset token for the given user.

    :param user: The user who requested the password reset.
    :param validity_period_in_hours: If set, the token will become invalid after the specified number of hours.
    """
    if validity_period_in_hours is not None:
        validity_period = datetime.timedelta(hours=float(validity_period_in_hours))
        expiry_date = timezone.now() + validity_period
    else:
        expiry_date = None

    _, token = PasswordResetToken.objects.create_key(
        user=user, 
        name=f"Password reset token for {user.email}",
        expiry_date=expiry_date
    )
    return token


def delete_password_reset_token(token: str) -> None:
    """Deletes the given password reset token if it exists"""
    try:
        reset_token: PasswordResetToken = PasswordResetToken.objects.get_from_key(token)
    except PasswordResetToken.DoesNotExist:
        pass
    else:
        reset_token.delete()
    return None


def check_password_reset_token_validity(token: str) -> bool:
    """
    Check if the password reset token is valid.

    :return: True if the token is valid, False otherwise.
    """
    try:
        reset_token: PasswordResetToken = PasswordResetToken.objects.get_from_key(token)
    except PasswordResetToken.DoesNotExist:
        return False
    if reset_token and reset_token.has_expired is False:
        return True
    return False


def reset_password_for_token(token: str, new_password: str) -> bool:
    """
    Reset the password for the user associated with the given password reset token.

    :param token: The password reset token.
    :param new_password: The new password.
    """
    try:
        reset_token: PasswordResetToken = PasswordResetToken.objects.get_from_key(token)
    except PasswordResetToken.DoesNotExist:
        return False
    if reset_token and reset_token.has_expired is False:
        user = reset_token.user
        user.set_password(new_password)
        user.save()
        # Delete the token after the password has been reset
        reset_token.delete()
        return True
    return False


def construct_password_reset_mail(
        user: UserAccount, 
        password_reset_url: str, 
        token: str, 
        token_name: str = "token",
        token_validity_period: Optional[int] = None,
    ) -> str:
    """
    Constructs the password reset mail body for the given user.

    :param user: The user who requested the password reset.
    :param password_reset_url: The URL where the user can reset the password.
    :param token: The password reset token.
    :param token_name: The name of the token parameter in the URL. The default value is "token".
    :return: The password reset mail body.
    """
    reset_link = f"{password_reset_url}?{token_name}={token}"
    context = {
        "webapp_name": settings.SITE_NAME,
        "email": user.email,
        "reset_link": reset_link,
        "validity_period": token_validity_period,
        "current_year": timezone.now().year,
    }
    return render_to_string("emails/password_reset_mail.html", context)


def get_token_owner(token: str) -> Optional[UserAccount]:
    """
    Get the user who owns the given password reset token.

    :param token: The password reset token.
    :return: The user who owns the token.
    """
    try:
        reset_token: PasswordResetToken = PasswordResetToken.objects.get_from_key(token)
    except PasswordResetToken.DoesNotExist:
        return None
    return reset_token.user

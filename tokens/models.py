from rest_framework_api_key.models import AbstractAPIKey
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings



class PasswordResetToken(AbstractAPIKey):
    """Make shift password reset token model"""
    name = models.CharField(
        max_length=200,
        blank=False,
        default=None,
        help_text=(
            "A free-form name for the token. "
            "Need not be unique. "
            "200 characters max."
        ),
    )
    revoked = models.BooleanField(
        blank=True,
        default=False,
        help_text=(
            "If the token is revoked, clients cannot use it anymore. "
            "(This cannot be undone.)"
        ),
    )
    expiry_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Expires",
        help_text="Once token expires, clients cannot use it anymore.",
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="password_reset_tokens")

    class Meta(AbstractAPIKey.Meta):
        verbose_name = _("Password Reset Token")
        verbose_name_plural = _("Password Reset Tokens")
        # Use a unique constraint to ensure that only one token per user is valid at a time
        unique_together = ["user", "hashed_key"]


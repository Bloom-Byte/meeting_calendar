from django.conf import settings
from django.db import models
import uuid
from django.shortcuts import resolve_url
from django.utils.translation import gettext_lazy as _

from .utils import generate_unique_identifier


class Link(models.Model):
    """
    Model to represent a wrapped URL
    """
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    identifier = models.CharField(
        default=generate_unique_identifier, max_length=10, 
        unique=True, help_text=_("The unique identifier for the URL")
    )
    url = models.URLField(_("URL"), help_text=_("The URL to be wrapped"))
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=_("Created by"), 
        on_delete=models.CASCADE, help_text=_("The user who created this link")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return self.identifier

    @property
    def path(self) -> str:
        """
        Returns a unique internal URL path for the link.

        This URL path does not change even if the wrapped URL changes.
        """
        return resolve_url("booking:session_link", self.identifier)

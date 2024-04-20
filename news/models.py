from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid
from django.conf import settings



class News(models.Model):
    """Model to represent news for application users"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    headline = models.CharField(max_length=255, help_text=_("Give a headline to the news"))
    content = models.TextField(help_text=_("Write the content of the news"))
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
        related_name="news", help_text=_("Author of the news"),
        blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "News"
        verbose_name_plural = "News"

    def __str__(self) -> str:
        return self.headline

from django.conf import settings
from django.db import models
import uuid
from django.utils.translation import gettext_lazy as _
from django_utz.decorators import model

from .managers import SessionManager


@model
class Session(models.Model):
    """Model to represent a booked meeting session"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_("Session title"), max_length=255, help_text=_("Give a title to the session"))
    start = models.DateTimeField(_("Starts"), help_text=_("When does this session start?"))
    end = models.DateTimeField(_("Ends"), help_text=_("When does this session end?"))
    booked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Booked by"), on_delete=models.CASCADE,
        help_text=_("Who booked this session?")
    )
    link = models.URLField(
        blank=True, null=True,
        help_text=_("Provide a link to the session if any")
    )
    is_pending = models.BooleanField(default=True, help_text=_("Has this session been held? If so, uncheck this."))
    cancelled = models.BooleanField(default=False, help_text=_("Check this if you want to cancel this session"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = SessionManager()

    class Meta:
        ordering = ["start"]
        verbose_name = _("Session")
        verbose_name_plural = _("Sessions")

    class UTZMeta:
        datetime_fields = "__all__"

    def __str__(self) -> str:
        return f"'{self.title}' - to hold from {self.time_period[0]} to {self.time_period[1]} on {self.date}"
    
    @property
    def duration(self) -> int:
        """Return the duration of the session in minutes"""
        return (self.end - self.start).seconds // 60
    
    @property
    def date(self) -> str:
        """Return the date of the session"""
        return self.start.strftime("%Y-%m-%d")
    
    @property
    def time_period(self) -> str:
        """Returns the start and end time of the session"""
        return self.start.strftime("%H:%M"), self.end.strftime("%H:%M")
    

    def save(self, *args, **kwargs):
        if self.start >= self.end:
            raise ValueError("End datetime must be greater than start datetime")
        if self.start.date() != self.end.date():
            raise ValueError("Start and end datetime must be on the same day")
        super().save(*args, **kwargs)



@model
class UnavailablePeriod(models.Model):
    """Model to represent a datetime period that is unavailable for booking"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    start = models.DateTimeField(_("From"), help_text=_("From what date and time you will be unavailable?"))
    end = models.DateTimeField(_("To"), help_text=_("Till what date and time you will be unavailable?"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["start"]
        verbose_name = _("Unavailable Period")
        verbose_name_plural = _("Unavailable Periods")
    
    class UTZMeta:
        datetime_fields = "__all__"

    def __str__(self) -> str:
        return f"Unavailable from {self.time_period[0]} to {self.time_period[1]} on {self.date}"
    
    @property
    def date(self) -> str:
        """Return the date of the unavailable period"""
        return self.start.strftime("%Y-%m-%d")
    
    @property
    def time_period(self) -> str:
        """Returns the start and end time of the unavailable period"""
        return self.start.strftime("%H:%M"), self.end.strftime("%H:%M")
    
    
    def save(self, *args, **kwargs):
        if self.start >= self.end:
            raise ValueError("End datetime must be greater than start datetime")
        if self.start.date() != self.end.date():
            raise ValueError("Start and end datetime must be on the same day")
        super().save(*args, **kwargs)

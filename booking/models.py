from django.conf import settings
from django.db import models
import uuid
from django.utils.translation import gettext_lazy as _
from django_utz.decorators import model
from django.utils import timezone
from typing import Optional

from .managers import SessionManager
from links.models import Link


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
    link = models.ForeignKey(
        Link, verbose_name=_("Link"), on_delete=models.SET_NULL,
        help_text=_("The link to the session"), null=True,
        related_name="session", blank=True
    )
    has_held = models.BooleanField(default=False, help_text=_("Has this session been held? If so, check this."))
    cancelled = models.BooleanField(default=False, help_text=_("Check this if you want to cancel this session"))
    rescheduled_at = models.DateTimeField(
        _("Rescheduled at"),  null=True, blank=True,
        help_text=_("When was this session date or time changed?")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = SessionManager()

    class Meta:
        ordering = ["-start__date", "start__time"]
        verbose_name = _("Session")
        verbose_name_plural = _("Sessions")

    class UTZMeta:
        datetime_fields = "__all__"
        attribute_suffix = "user_tz"

    def __str__(self) -> str:
        return f"'{self.title}' with {self.booked_by.fullname} ({self.booked_by.email})"
    
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
    
    @property
    def is_pending(self) -> bool:
        """Returns True if the session has not been held, else False"""
        return not self.has_held and not self.cancelled
    
    @property
    def is_approved(self) -> bool:
        """
        Returns True if the session is pending and has a link attached

        This means that the admin has approved the session and the session
        can be held.
        """
        return self.is_pending and self.link is not None
    

    def was_missed(self, tz: Optional[timezone.tzinfo] = None) -> bool:
        """
        Returns True if the session was missed. That is, if the session is still
        pending even after it's end datetime, although a session link was attached.
        """
        return self.end <= timezone.now().astimezone(tz) and self.is_pending and self.link
    

    def save(self, *args, **kwargs):
        if self.start >= self.end:
            raise ValueError("End datetime must be greater than start datetime")
        if self.start.date() != self.end.date():
            raise ValueError("Start and end datetime must be on the same day")
        
        # Check if the session has been rescheduled
        old_instance = Session.objects.filter(pk=self.pk).first()
        if old_instance:
            schedule_changed = old_instance.start != self.start or old_instance.end != self.end
            if schedule_changed:
                self.rescheduled_at = timezone.now()
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
        attribute_suffix = "user_tz"

    def __str__(self) -> str:
        return f"Unavailable from {self.start} to {self.end}"
    
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


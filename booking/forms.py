from typing import Any, Dict
from django import forms
from timezone_field.forms import TimeZoneFormField
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import datetime
from django.contrib.auth import get_user_model
from django_utz.middleware import get_request_user

from . import models
from links.models import Link
from links.forms import LinkForm
from .utils import check_if_time_period_is_available

UserModel = get_user_model()


class BaseBookingModelForm(forms.ModelForm):
    """Base model form for models in booking app"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request_user = get_request_user()
        # Always set the initial timezone in the form to the request user's timezone
        self.initial["timezone"] = request_user.timezone
        # When the form is displaying the data of the model instance
        # to the user, display the fields below in the request user's timezone
        if self.instance.pk:
            try:
                # django-utz will automatically adds datetime fields with the suffix `user_tz`
                # which are in the preferred timezone (the request user's timezone)
                self.initial['date'] = self.instance.start_user_tz.strftime("%Y-%m-%d")
                self.initial["start_time"] = self.instance.start_user_tz.strftime("%H:%M")
                self.initial["end_time"] = self.instance.end_user_tz.strftime("%H:%M")
            except (AttributeError, TypeError):
                pass


    def clean(self) -> Dict[str, Any]:
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time", None)
        end_time = cleaned_data.get("end_time", None)
        date = cleaned_data.get("date", None)
        tz = cleaned_data.get("timezone", None)

        if start_time and end_time:
            if start_time >= end_time:
                self.add_error("start_time", "Start time must be less than end time")

        if date and start_time and end_time:
            start = datetime.datetime.combine(date=date, time=start_time, tzinfo=tz).astimezone()
            end = datetime.datetime.combine(date=date, time=end_time, tzinfo=tz).astimezone()
            # If the object is just being created, check if the start time is in the past
            # If so, raise an error
            if not self.instance.pk:
                now = timezone.now().astimezone(tz)
                if start < now:
                    self.add_error("date", "Start time cannot be in the past")

            # Check if the period booked is available, that is, the period
            # is not already booked by another session or set as unavailable
            # Exclude the current session if it is being updated
            if isinstance(self.instance, models.Session) and self.instance.pk:
                excluded_sessions = (self.instance,)
            else:
                excluded_sessions = None
            time_period_is_available = check_if_time_period_is_available(start, end, excluded_sessions)
            if time_period_is_available is False:
                raise forms.ValidationError(
                    "The time period chosen is not available. Please choose another time period."
                )
            # Update the cleaned data with the start and end datetime objects
            cleaned_data["start"] = start
            cleaned_data["end"] = end
        return cleaned_data
    

    def save(self, commit: bool = True):
        instance = super().save(commit=False)
        instance.start = self.cleaned_data["start"]
        instance.end = self.cleaned_data["end"]
        if commit:
            instance.save()
        return instance



class SessionForm(BaseBookingModelForm):
    """
    Form for creating and updating sessions. Always use this form to create and update sessions.

    Contains necessary validations and checks to ensure that the session is created or updated correctly.
    """
    class Meta:
        model = models.Session
        fields = [
            "title", "date", "start_time", 
            "end_time", "timezone", "booked_by", 
            "link", "has_held", "cancelled",
            "rescheduled_at"
        ]
        labels = {
            "cancelled": _("Cancel session"),
            "has_held": _("Mark as held")
        }

    date = forms.DateField(
        input_formats=["%Y-%m-%d"], required=True, label=_("Date"), disabled=False,
        widget=forms.DateInput(
            attrs={
                "type": "date", 
                "min": timezone.now().strftime("%Y-%m-%d")
            },
            format="yyyy-mm-dd",
        ),
        help_text=_("The date the session will take place (in your timezone).")
    )
    start_time = forms.TimeField(
        input_formats=["%H:%M", "%H:%M:%S"], required=True, disabled=False,
        widget=forms.TimeInput(attrs={
            "type": "time",
        }),
        label=_("Starts at"), help_text=_("The time the session will start (in your timezone).")
    )
    end_time = forms.TimeField(
        input_formats=["%H:%M", "%H:%M:%S"], required=True, disabled=False,
        widget=forms.TimeInput(attrs={
            "type": "time",
            "max": "23:59"
        }),
        label=_("Ends at"), help_text=_("The time the session will end (in your timezone).")
    )
    timezone = TimeZoneFormField(
        required=True, label=_("Timezone"),
        help_text=_("Your timezone"), disabled=True
    )
    link = forms.CharField(
        required=False, label=_("Meeting Link"),
        help_text=_("The link the user will use to join the session meeting"),
        empty_value=None
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            try:
                link = self.instance.link
                self.initial["link"] = link.url if link else None
                self.initial["rescheduled_at"] = self.instance.rescheduled_at_user_tz
            except (AttributeError, TypeError):
                pass


    def clean(self) -> None:
        cleaned_data = super().clean()
        link = cleaned_data["link"]
        has_held = cleaned_data.get("has_held", False)
        cancelled = cleaned_data.get("cancelled", False)
        tz = cleaned_data.get("timezone")
        request_user = get_request_user()
         
        if link:
            if self.instance.link:
                # If instance already has a link attached,
                # update the link if any change has occurred
                link_form = LinkForm(instance=self.instance.link, data={"url": link})
                if link_form.has_changed():
                    cleaned_data["link"] = link_form.save()
                else:
                    # Set the link to the instance's link
                    cleaned_data["link"] = self.instance.link
            else:
                # Else, create a new Link object and attach it to the instance
                link_form = LinkForm(data={"url": link})
                if link_form.is_valid():
                    cleaned_data["link"] = link_form.save()
                else:
                    self.add_error("link", "Invalid URL")
        else:
            # If the link is not set, set it to None
            cleaned_data["link"] = None


        if request_user.is_admin:
            if has_held is True and not link:
                raise forms.ValidationError(
                    "You cannot mark a session as held when it does not have a link attached in the first place."
                )
            if has_held is True and cancelled is True:
                raise forms.ValidationError("You cannot cancel a session that has already been held")
            
        else:
            # If the user is not an admin, they cannot mark a session has held.
            if "has_held" in self.changed_data:
                raise forms.ValidationError("Only admins can mark a session as held.")
            else:
                # If "has_held" was not changed by the non-admin user, and the session was already marked as held by an
                # admin, then the user can't edit the session
                if has_held is True:
                    raise forms.ValidationError("You cannot edit a session that has already been held")

            # If the user is not an admin, they cannot cancel a session 
            if "cancelled" in self.changed_data:
                raise forms.ValidationError("Only admins can cancel a session.")
            else:
                # If "cancelled" was not changed by the non-admin user, and the session was already cancelled by an
                # admin, then the user can't edit the session
                if cancelled is True:
                    raise forms.ValidationError("You cannot edit a session that has already been cancelled")


        # Check if the session has been marked as held before it ends
        # If so, raise an error
        # Session edn datetime is already in the user's timezone from the parent `clean` method
        session_end_in_tz = cleaned_data.get("end", None)
        if session_end_in_tz:
            time_now_in_tz = timezone.now().astimezone(tz)
            if has_held is True and time_now_in_tz < session_end_in_tz:
                self.add_error("has_held", "You cannot mark a session as held before it ends.")
        return cleaned_data



class UnavailablePeriodAdminForm(BaseBookingModelForm):
    """Strictly for manipulating the unavailable period model in the admin panel"""
    class Meta:
        model = models.UnavailablePeriod
        fields = [
            "date", "start_time", 
            "end_time", "timezone"
        ]

    date = forms.DateField(
        input_formats=["%Y-%m-%d"], label=_("Date"), required=True,
        widget=forms.DateInput(
            attrs={
                "type": "date", 
                "min": timezone.now().strftime("%Y-%m-%d")
            },
            format="yyyy-mm-dd",
        ),
        help_text=_("On what date you will be unavailable?")
    )
    start_time = forms.TimeField(
        input_formats=["%H:%M", "%H:%M:%S"], label=_("From"), required=True,
        widget=forms.TimeInput(attrs={
            "type": "time",
        }),
        help_text=_("From what time you will be unavailable?")
    )
    end_time = forms.TimeField(
        input_formats=["%H:%M", "%H:%M:%S"], label=_("Till"), required=True,
        widget=forms.TimeInput(attrs={
            "type": "time",
            "max": "23:59"
        }),
        help_text=_("Till what time you will be unavailable?")
    )
    timezone = TimeZoneFormField(
        label=_("Timezone"), required=True,
        help_text=_("Your timezone."),
        disabled=True
    )

    

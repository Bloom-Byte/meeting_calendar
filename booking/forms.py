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
                start_date_in_user_tz = request_user.to_local_timezone(self.instance.start)
                end_date_in_user_tz = request_user.to_local_timezone(self.instance.end)
                self.initial['date'] = start_date_in_user_tz.strftime("%Y-%m-%d")
                self.initial["start_time"] = start_date_in_user_tz.strftime("%H:%M")
                self.initial["end_time"] = end_date_in_user_tz.strftime("%H:%M")
            except (AttributeError, TypeError):
                pass


    def clean(self) -> Dict[str, Any]:
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time", None)
        end_time = cleaned_data.get("end_time", None)
        date = cleaned_data.get("date", None)
        tz = cleaned_data.get("timezone")
        has_held = cleaned_data.get("has_held", False)

        if start_time and end_time:
            if start_time >= end_time:
                self.add_error("start_time", "Start time must be less than end time")

        if date and start_time and end_time:
            start = datetime.datetime.combine(date=date, time=start_time, tzinfo=tz).astimezone()
            end = datetime.datetime.combine(date=date, time=end_time, tzinfo=tz).astimezone()

            # Check if the start time is in the past, if so, raise an error
            # The user cannot book a session in the past
            if start < timezone.now().astimezone(tz):
                self.add_error("date", "You cannot book a session in the past")

            # Check if there are no sessions booked within the unavailable period
            # Or if no other unavailable period overlaps with the current one
            time_period_is_available = check_if_time_period_is_available(
                start=start, 
                end=end, 
                # Exclude the current session if it is being updated
                exclude_sessions=[self.instance] if self.instance.pk else None
            )
            if not time_period_is_available:
                raise forms.ValidationError(
                    "The time period chosen is not available. Please choose another time period."
                )
            cleaned_data["start"] = start
            cleaned_data["end"] = end

        # Check if the session has been marked as held before it ends
        # If so, raise an error
        session_end_in_tz = cleaned_data.get("end", None)
        if session_end_in_tz:
            time_now_in_tz = timezone.now().astimezone(tz)
            if has_held is True and time_now_in_tz < session_end_in_tz:
                self.add_error("has_held", "You cannot mark a session as held before it ends.")
        return cleaned_data
    

    def save(self, commit: bool = True) -> models.Session:
        instance = super().save(commit=False)
        instance.start = self.cleaned_data["start"]
        instance.end = self.cleaned_data["end"]
        if commit:
            instance.save()
        return instance



class SessionForm(BaseBookingModelForm):
    """Form for creating a new session"""
    class Meta:
        model = models.Session
        fields = [
            "title", "date", "start_time", 
            "end_time", "timezone", "booked_by", 
            "link", "has_held", "cancelled"
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
        required=False, label=_("Link"),
        help_text=_("The link to the session"),
        empty_value=None
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        link: Link = self.instance.link
        if link:
            self.initial["link"] = link.url


    def clean(self) -> None:
        cleaned_data = super().clean()
        link = cleaned_data["link"]
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

    

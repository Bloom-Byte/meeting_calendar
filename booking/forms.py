from typing import Any, Dict
from django import forms
from timezone_field.forms import TimeZoneFormField
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import datetime
from django.contrib.auth import get_user_model

from . import models
from links.models import Link
from links.forms import LinkForm

UserModel = get_user_model()


class BaseModelForm(forms.ModelForm):
    """Base model form for models in booking app"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.initial['date'] = self.instance.date
            self.initial["start_time"] = self.instance.time_period[0]
            self.initial["end_time"] = self.instance.time_period[1]
            self.initial["timezone"] = self.instance.start.tzinfo
        except AttributeError:
            pass


    def clean(self) -> Dict[str, Any]:
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        date = cleaned_data.get("date")
        timezone = cleaned_data.get("timezone")
        if start_time and end_time:
            if start_time >= end_time:
                self.add_error("start_time", "Start time cannot be greater than end time")

        cleaned_data["start"] = datetime.datetime.combine(date=date, time=start_time, tzinfo=timezone).astimezone()
        cleaned_data["end"] = datetime.datetime.combine(date=date, time=end_time, tzinfo=timezone).astimezone()
        return cleaned_data
    

    def save(self, commit: bool = True) -> models.Session:
        instance = super().save(commit=False)
        instance.start = self.cleaned_data["start"]
        instance.end = self.cleaned_data["end"]
        if commit:
            instance.save()
        return instance



class SessionForm(BaseModelForm):
    """Form for creating a new session"""
    class Meta:
        model = None
        fields = [
            "title", "date", "start_time", 
            "end_time", "timezone", "booked_by", 
            "link", "is_pending", "cancelled"
        ]

    date = forms.DateField(
        input_formats=["%Y-%m-%d"], required=True, label=_("Date"),
        widget=forms.DateInput(
            attrs={
                "type": "date", 
                "min": timezone.now().strftime("%Y-%m-%d")
            },
            format="yyyy-mm-dd",
        ),
        help_text=_("What date the session will take place? Select the date from the date picker")
    )
    start_time = forms.TimeField(
        input_formats=["%H:%M"], required=True,
        widget=forms.TimeInput(attrs={
            "type": "time",
            "min": timezone.now().strftime("%H:%M")
        }),
        label=_("Starts at"), help_text=_("What time the session will start? Format: HH:MM")
    )
    end_time = forms.TimeField(
        input_formats=["%H:%M"], required=True,
        widget=forms.TimeInput(attrs={"type": "time"}),
        label=_("Ends at"), help_text=_("What time the session will end? Format: HH:MM")
    )
    timezone = TimeZoneFormField(
        required=True, label=_("Timezone"),
        help_text=_("What's your timezone? Select the timezone from the dropdown menu")
    )
    link = forms.CharField(
        required=False, label=_("Link"),
        help_text=_("The link to the session"),
        empty_value=None
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["booked_by"].queryset = UserModel.objects.filter(is_active=True)
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
                # Else, create a new Link and attach it to the instance
                link_form = LinkForm(data={"url": link})
                if link_form.is_valid():
                    cleaned_data["link"] = link_form.save()
                else:
                    self.add_error("link", "Invalid URL")
        else:
            cleaned_data["link"] = None
        return cleaned_data



class UnavailablePeriodForm(BaseModelForm):
    """Form for creating an unavailable period"""
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
        help_text=_("On what date you will be unavailable? Select the date from the date picker")
    )
    start_time = forms.TimeField(
        input_formats=["%H:%M"], label=_("From"), required=True,
        widget=forms.TimeInput(attrs={
            "type": "time",
            "min": timezone.now().strftime("%H:%M")
        }),
        help_text=_("From what time you will be unavailable? Format: HH:MM")
    )
    end_time = forms.TimeField(
        input_formats=["%H:%M"], label=_("Till"), required=True,
        widget=forms.TimeInput(attrs={"type": "time"}),
        help_text=_("Till what time you will be unavailable? Format: HH:MM")
    )
    timezone = TimeZoneFormField(
        label=_("Timezone"), required=True,
        help_text=_("What's your timezone? Select the timezone from the dropdown menu")
    )

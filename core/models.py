from django.db import models
from django.utils.translation import gettext_lazy as _
from django_utz.decorators import model
import datetime
try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo
from timezone_field import TimeZoneField



@model
class BusinessHoursSettings(models.Model):
    id = models.BigAutoField(primary_key=True)
    opens_at = models.TimeField(
        _("Business opens at"), help_text=_("The time the business opens"), 
        default=datetime.time.fromisoformat("08:00:00")
    )
    closes_at = models.TimeField(
        _("Business closes at"), help_text=_("The time the business closes"), 
        default=datetime.time.fromisoformat("20:00:00")
    )
    timezone = TimeZoneField(default=zoneinfo.ZoneInfo("UTC"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Business Hours Settings")
        verbose_name_plural = _("Business Hours Settings")
        ordering = ["-created_at"]

    class UTZMeta:
        datetime_fields = "__all__"
        attribute_suffix = "user_tz"

    def __str__(self) -> str:
        return f"Business opens at {self.opens_at} and closes at {self.closes_at} ({self.timezone})"

    
    @property
    def opens_at_today(self) -> datetime.datetime:
        """Returns the opening time for today"""
        # Should be in the business' timezone
        return datetime.datetime.combine(datetime.date.today(), self.opens_at, tzinfo=self.timezone)
    
    @property
    def closes_at_today(self) -> datetime.datetime:
        """Returns the closing time for today"""
        # Should be in the business' timezone
        return datetime.datetime.combine(datetime.date.today(), self.closes_at, tzinfo=self.timezone)

    
    def time_is_within_business_hours_today(self, time: datetime.time, tz: datetime.tzinfo) -> bool:
        """Returns True if the time is within the business hours for today"""
        # convert the time to a datetime with today's and the time given in the timezone
        dt = datetime.datetime.combine(datetime.date.today(), time, tzinfo=tz)
        return self.opens_at_today <= dt.astimezone(self.timezone) <= self.closes_at_today


    def datetime_is_within_business_hours(self, dt: datetime.datetime) -> bool:
        """Checks if the given datetime is within the business hours (considers timezone differences)"""
        date_from_dt = dt.date()
        opens_at_on_date = datetime.datetime.combine(date_from_dt, self.opens_at, tzinfo=self.timezone)
        closes_at_on_date = datetime.datetime.combine(date_from_dt, self.closes_at, tzinfo=self.timezone)
        return opens_at_on_date <= dt.astimezone(self.timezone) <= closes_at_on_date


from typing import Dict, List, Optional, Any
from django.utils import timezone
import datetime
from django.db import models

from .models import Session, UnavailablePeriod
from .managers import SessionQuerySet
from users.models import UserAccount


def get_unavailable_times_for_date(date: str, tz: Optional[timezone.tzinfo] = None) -> List[str]:
    """
    Return a list of unavailable times for the given date and timezone
    """
    if tz:
        date = timezone.datetime.strptime(date, "%Y-%m-%d").astimezone(tz).strftime("%Y-%m-%d")
    # Get unavailable times
    unavailable_times = []
    unavailable_periods = UnavailablePeriod.objects.filter(start__date=date)
    for unavailable_period in unavailable_periods:
        start_in_tz = unavailable_period.start.astimezone(tz).strftime("%H:%M")
        end_in_tz = unavailable_period.end.astimezone(tz).strftime("%H:%M")
        unavailable_times.append([start_in_tz, end_in_tz])

    # Get booked times
    booked_times = []
    booked_sessions = Session.objects.exclude(cancelled=True).filter(start__date=date)
    for session in booked_sessions:
        start_in_tz = session.start.astimezone(tz).strftime("%H:%M")
        end_in_tz = session.end.astimezone(tz).strftime("%H:%M")
        booked_times.append([start_in_tz, end_in_tz])
    return [*unavailable_times, *booked_times]



def get_sessions_on_date_booked_by_user(date: str, user: UserAccount):
    """
    Return a list of booked sessions for the given date and user
    """
    date = timezone.datetime.strptime(date, "%Y-%m-%d").astimezone(user.utz).strftime("%Y-%m-%d")
    return Session.objects.filter(start__date=date, booked_by=user)



def get_time_periods_on_date_booked_by_user(date: str, user: UserAccount) -> Dict[str, Dict[str, Any]]:
    todays_sessions: SessionQuerySet[Session] = get_sessions_on_date_booked_by_user(date, user)
    tz = user.utz
    pending_sessions = todays_sessions.pending()
    missed_sessions = todays_sessions.missed(tz=user.utz)
    cancelled_sessions = todays_sessions.cancelled()
    held_sessions = todays_sessions.filter(has_held=True)
    pending = {}
    missed = {}
    cancelled = {}
    held = {}
    for session in pending_sessions:
        if session not in missed_sessions:
            start_in_tz = session.start.astimezone(tz).strftime("%H:%M")
            end_in_tz = session.end.astimezone(tz).strftime("%H:%M")
            pending[session.title] = {
                "id": session.pk,
                "time_period": [start_in_tz, end_in_tz],
                "date": date,
                "link": session.link.path if session.link else None
            }

    for session in missed_sessions:
        start_in_tz = session.start.astimezone(tz).strftime("%H:%M")
        end_in_tz = session.end.astimezone(tz).strftime("%H:%M")
        missed[session.title] = {
            "id": session.pk,
            "time_period": [start_in_tz, end_in_tz],
            "date": date,
            "link": session.link.path if session.link else None
        }
    
    for session in cancelled_sessions:
        start_in_tz = session.start.astimezone(tz).strftime("%H:%M")
        end_in_tz = session.end.astimezone(tz).strftime("%H:%M")
        cancelled[session.title] = {
            "id": session.pk,
            "time_period": [start_in_tz, end_in_tz],
            "date": date,
            "link": session.link.path if session.link else None
        }

    for session in held_sessions:
        start_in_tz = session.start.astimezone(tz).strftime("%H:%M")
        end_in_tz = session.end.astimezone(tz).strftime("%H:%M")
        held[session.title] = {
            "id": session.pk,
            "time_period": [start_in_tz, end_in_tz],
            "date": date,
            "link": session.link.path if session.link else None
        }
    return {
        "pending": pending,
        "missed": missed,
        "cancelled": cancelled,
        "held": held
    }


def get_unavailable_periods_within_time_period(start: timezone.datetime, end: timezone.datetime):
    """
    Returns all unavailable periods that fall within the given (time period) start and end datetime

    :param start: Start datetime of the time period
    :param end: End datetime of the time period
    """
    q = models.Q(start__range=(start, end)) | models.Q(end__range=(start, end))
    return UnavailablePeriod.objects.filter(q)


def get_sessions_booked_within_time_period(start: datetime.datetime, end: datetime.datetime):
    """
    Return the session booked by the user within the given time period

    :param start: Start datetime of the time period
    :param end: End datetime of the time period
    """
    q = models.Q(start__range=(start, end)) | models.Q(end__range=(start, end))
    return Session.objects.filter(q)


def get_overlapping_unavailable_periods(instance: UnavailablePeriod):
    """
    Returns all existing unavailable periods with start and end datetime overlap with the 
    start and end datetime of the given instance

    :param instance: UnavailablePeriod instance
    """
    time_period = [instance.start, instance.end]
    unavailable_periods_within_time_period = get_unavailable_periods_within_time_period(*time_period)
    return unavailable_periods_within_time_period.exclude(pk=instance.pk)


def check_if_time_period_is_available(start: datetime.datetime, end: datetime.datetime) -> bool:
    """
    Check if the time period is available for booking. That is,
    if there are no sessions booked within the time period 
    and no unavailable period overlaps with it.

    :param start: Start datetime of the time period
    :param end: End datetime of the time period
    :returns: True if the time period is available for booking, False otherwise
    """
    booked = get_sessions_booked_within_time_period(start, end).exists()
    unavailable = get_unavailable_periods_within_time_period(start, end).exists()
    return not booked and not unavailable

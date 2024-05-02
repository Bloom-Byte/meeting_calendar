from typing import Dict, List, Optional, Any
from django.utils import timezone
import datetime
from django.db import models

from .models import Session, UnavailablePeriod
from .managers import SessionQuerySet
from users.models import UserAccount



def session_to_simple_dict(session: Session, tz: Optional[datetime.tzinfo] = None) -> Dict[str, Any]:
    """Parse the session object to a simple dictionary with the necessary fields"""
    start_in_tz = session.start.astimezone(tz).strftime("%H:%M")
    end_in_tz = session.end.astimezone(tz).strftime("%H:%M")
    return {
        "id": session.pk,
        "date": session.start.strftime("%Y-%m-%d"),
        "time_period": [start_in_tz, end_in_tz],
        "link": session.link.path if session.link else None,
        "is_approved": session.is_approved,
    }


def _get_objects_where_start_date_equals_given_date_in_users_tz(qs: models.QuerySet, user: UserAccount, date: datetime.date):
    todays_objs_pks = []
    for obj in qs:
        start_in_user_tz = user.to_local_timezone(obj.start)
        if start_in_user_tz.date() == date:
            todays_objs_pks.append(obj.pk)
    return qs.filter(pk__in=todays_objs_pks)


def get_unavailable_times_on_date_for_user(date: str, user: UserAccount) -> List[str]:
    """
    Return a list of unavailable times for the given date in the give user's timezone

    :param date: Date in the format "YYYY-MM-DD"
    """
    date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    # Get unavailable times on given date
    unavailable_times = []
    unavailable_periods_on_date_in_user_tz = _get_objects_where_start_date_equals_given_date_in_users_tz(
        qs=UnavailablePeriod.objects.all(),
        user=user, date=date
    )
    for unavailable_period in unavailable_periods_on_date_in_user_tz:
        start_in_tz = unavailable_period.start.astimezone(user.utz).strftime("%H:%M")
        end_in_tz = unavailable_period.end.astimezone(user.utz).strftime("%H:%M")
        unavailable_times.append([start_in_tz, end_in_tz])

    # Get booked times  on given date
    booked_times = []
    valid_sessions = Session.objects.exclude(cancelled=True)
    sessions_booked_on_date_in_user_tz = _get_objects_where_start_date_equals_given_date_in_users_tz(
        qs=valid_sessions,
        user=user, date=date
    )
    for session in sessions_booked_on_date_in_user_tz:
        session_dict = session_to_simple_dict(session, user.utz)
        booked_times.append(session_dict["time_period"])
    return [*unavailable_times, *booked_times]


def get_sessions_booked_on_date_by_user(date: str, user: UserAccount):
    """
    Return a list of booked sessions for the given date in the given user's timezone
    """
    date = timezone.datetime.strptime(date, "%Y-%m-%d").date()
    sessions_booked_by_user = Session.objects.filter(booked_by=user)

    return _get_objects_where_start_date_equals_given_date_in_users_tz(
        qs=sessions_booked_by_user,
        user=user, date=date
    )


def get_bookings_by_user_on_date(date: str, user: UserAccount) -> Dict[str, Dict[str, Any]]:
    """
    Returns a dictionary containing sessions booked by users on the given date
    sorted into categories
    """
    tz = user.utz
    todays_sessions: SessionQuerySet[Session] = get_sessions_booked_on_date_by_user(date, user)
    pending_sessions = todays_sessions.pending()
    missed_sessions = todays_sessions.missed(tz=tz)
    cancelled_sessions = todays_sessions.cancelled()
    held_sessions = todays_sessions.filter(has_held=True)
    pending = {}
    missed = {}
    cancelled = {}
    held = {}
    for session in pending_sessions:
        if session not in missed_sessions:
            pending[session.title] = session_to_simple_dict(session, tz)

    for session in missed_sessions:
        missed[session.title] = session_to_simple_dict(session, tz)
    
    for session in cancelled_sessions:
        cancelled[session.title] = session_to_simple_dict(session, tz)

    for session in held_sessions:
        held[session.title] = session_to_simple_dict(session, tz)
    return {
        "pending": pending,
        "missed": missed,
        "cancelled": cancelled,
        "held": held
    }


def remove_booked_time_periods_from_unavailable_times(
        bookings: Dict[str, Dict[str, Any]], 
        unavailable_time_periods: List[List[str]]
    ):
    """Removes all time periods that are already part of the bookings data from the unavailable times list"""
    for val in bookings.values():
        for data in val.values():
            time_period = data["time_period"]
            if data["time_period"] in unavailable_time_periods:
                unavailable_time_periods.remove(time_period)
    return None


def get_unavailable_periods_within_time_period(start: datetime.datetime, end: datetime.datetime):
    """
    Returns all unavailable periods that fall within the given (time period) start and end datetime

    :param start: Start datetime of the time period
    :param end: End datetime of the time period
    """
    q = models.Q(start__gt=start, start__lt=end) | models.Q(end__gt=start, end__lt=end)
    return UnavailablePeriod.objects.filter(q)


def get_sessions_booked_within_time_period(start: datetime.datetime, end: datetime.datetime):
    """
    Return the session booked by the user within the given time period

    :param start: Start datetime of the time period
    :param end: End datetime of the time period
    """
    q = models.Q(start__gt=start, start__lt=end) | models.Q(end__gt=start, end__lt=end)
    return Session.objects.filter(q)


def get_overlapping_unavailable_periods(instance: UnavailablePeriod):
    """
    Returns all existing unavailable periods with start and end datetime overlap with the 
    start and end datetime of the given instance

    :param instance: UnavailablePeriod instance
    """
    time_period = (instance.start, instance.end)
    unavailable_periods_within_time_period = get_unavailable_periods_within_time_period(*time_period)
    return unavailable_periods_within_time_period.exclude(pk=instance.pk)


def check_if_time_period_is_available(start: datetime.datetime, end: datetime.datetime, exclude_sessions: Optional[List[Session]] = None) -> bool:
    """
    Check if the time period is available for booking. That is,
    if there are no sessions booked within the time period 
    and no unavailable period overlaps with it.

    :param start: Start datetime of the time period
    :param end: End datetime of the time period
    :param exclude_sessions: These sessions will not be considered when checking for availability
    of the time period.
    :returns: True if the time period is available for booking, False otherwise
    """
    exclude_sessions = exclude_sessions or []
    booked = get_sessions_booked_within_time_period(start, end).exclude(
        pk__in=[session.pk for session in exclude_sessions]
    ).exists()
    unavailable = get_unavailable_periods_within_time_period(start, end).exists()
    return not booked and not unavailable


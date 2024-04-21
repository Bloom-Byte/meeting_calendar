from typing import List, Optional
from django.utils import timezone

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
    booked_sessions = Session.objects.filter(start__date=date)
    for session in booked_sessions:
        start_in_tz = session.start.astimezone(tz).strftime("%H:%M")
        end_in_tz = session.end.astimezone(tz).strftime("%H:%M")
        booked_times.append([start_in_tz, end_in_tz])
    return unavailable_times + booked_times



def get_sessions_on_date_booked_by_user(date: str, user: UserAccount):
    """
    Return a list of booked sessions for the given date and user
    """
    date = timezone.datetime.strptime(date, "%Y-%m-%d").astimezone(user.utz).strftime("%Y-%m-%d")
    return Session.objects.filter(start__date=date, booked_by=user)



def get_time_periods_on_date_booked_by_user(date: str, user: UserAccount):
    todays_sessions: SessionQuerySet[Session] = get_sessions_on_date_booked_by_user(date, user)
    tz = user.utz
    pending_sessions = todays_sessions.pending()
    missed_sessions = todays_sessions.missed()
    cancelled_sessions = todays_sessions.cancelled()
    held_sessions = todays_sessions.filter(has_held=True)
    pending = {}
    missed = {}
    cancelled = {}
    held = {}
    for session in pending_sessions:
        start_in_tz = session.start.astimezone(tz).strftime("%H:%M")
        end_in_tz = session.end.astimezone(tz).strftime("%H:%M")
        pending[session.title] = [start_in_tz, end_in_tz]

    for session in missed_sessions:
        start_in_tz = session.start.astimezone(tz).strftime("%H:%M")
        end_in_tz = session.end.astimezone(tz).strftime("%H:%M")
        missed[session.title] = [start_in_tz, end_in_tz]
    
    for session in cancelled_sessions:
        start_in_tz = session.start.astimezone(tz).strftime("%H:%M")
        end_in_tz = session.end.astimezone(tz).strftime("%H:%M")
        cancelled[session.title] = [start_in_tz, end_in_tz]

    for session in held_sessions:
        start_in_tz = session.start.astimezone(tz).strftime("%H:%M")
        end_in_tz = session.end.astimezone(tz).strftime("%H:%M")
        held[session.title] = [start_in_tz, end_in_tz]
    return {
        "pending": pending,
        "missed": missed,
        "cancelled": cancelled,
        "held": held
    }

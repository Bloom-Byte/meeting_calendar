from typing import List
from .models import Session, UnavailablePeriod


def get_unavailable_times_for_date(date: str) -> List[str]:
    """Return a list of unavailable times for the given date"""
    # Get unavailable times
    unavailable_times = [
        unavailable_period.time_period
        for unavailable_period in UnavailablePeriod.objects.filter(start__date=date)
    ]

    # Get booked times
    booked_times = [
        session.time_period
        for session in Session.objects.filter(start__date=date)
    ]
    return unavailable_times + booked_times

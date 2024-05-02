from os import name
from django.utils import timezone
from django.db import models

from users.models import UserAccount
from booking.managers import SessionQuerySet
from news.models import News



def get_future_sessions_for_user(session_qs: SessionQuerySet, user: UserAccount) -> SessionQuerySet:
    """
    Return all future pending sessions for the user (in the user's timezone).

    The sessions are marked as missed if they are missed.

    :param session_qs: Queryset of Session objects
    :param user: UserAccount instance
    """
    user_qs = session_qs.filter(booked_by=user)
    pending_sessions = user_qs.pending()
    date_now = timezone.now().astimezone(user.utz).date()
    future_sessions = pending_sessions.start_date_gte(date_now)
    missed_sessions = future_sessions.missed(tz=user.utz)
    for session in future_sessions:
        if session in missed_sessions:
            session.missed = True
        else:
            session.missed = False
    return future_sessions


def get_todays_news_for_user(news_qs: models.QuerySet[News], user: UserAccount) -> models.QuerySet[News]:
    """
    Return news for the user that were created today (in the user's timezone)

    :param news_qs: Queryset of News objects
    :param user: UserAccount instance
    """
    today_user_tz = user.to_local_timezone(timezone.now())
    return news_qs.filter(display_at__date=today_user_tz.date())

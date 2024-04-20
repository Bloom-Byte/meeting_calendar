from django.utils import timezone
from django.db import models

from users.models import UserAccount
from booking.managers import SessionQuerySet
from news.models import News



def get_todays_sessions_for_user(session_qs: SessionQuerySet, user: UserAccount) -> SessionQuerySet:
    """
    Return today's pending sessions for the user (in the user's timezone).

    The sessions are marked as missed if they are missed. Only sessions with a link are returned.

    :param session_qs: Queryset of Session objects
    :param user: UserAccount instance
    """
    user_qs = session_qs.filter(booked_by=user)
    pending_sessions = user_qs.pending()
    todays_sessions = pending_sessions.today(tz=user.utz).has_link()
    missed_sessions = todays_sessions.missed(tz=user.utz)
    for session in todays_sessions:
        if session in missed_sessions:
            session.missed = True
        else:
            session.missed = False
    return todays_sessions


def get_todays_news_for_user(news_qs: models.QuerySet[News], user: UserAccount) -> models.QuerySet[News]:
    """
    Return news for the user that were created today (in the user's timezone)

    :param news_qs: Queryset of News objects
    :param user: UserAccount instance
    """
    today = user.to_local_timezone(timezone.now())
    return news_qs.filter(created_at__date=today.date())

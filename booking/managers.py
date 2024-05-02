from typing import Optional
from django.db import models
from django.db.models.manager import BaseManager
from django.utils import timezone
import datetime


class SessionQuerySet(models.QuerySet):
    """Custom queryset for the Session model"""

    def pending(self):
        """
        Returns sessions that have not been held and have not been not cancelled
        """
        return self.filter(has_held=False, cancelled=False)
    

    def has_link(self):
        """Returns only sessions with a link attached"""
        return self.exclude(link__isnull=True)
    

    def approved(self):
        """Returns sessions that are pending and already have a session link attached"""
        return self.pending().has_link()
    

    def unapproved(self):
        """Returns sessions that are pending and do not have a session link attached"""
        return self.pending().filter(link__isnull=True)


    def missed(self, tz: Optional[timezone.tzinfo] = None):
        """
        Returns approved sessions that were missed. That is, sessions that 
        have not been held even after their end datetime, although they have
        a link attached.
        """
        return self.approved().filter(end__lte=timezone.now().astimezone(tz))
    

    def cancelled(self):
        """Returns sessions that have been cancelled"""
        return self.filter(cancelled=True)
    

    def today(self, tz: Optional[timezone.tzinfo] = None):
        """
        Returns sessions that are scheduled for today

        :param tz: Timezone to use for filtering
        """
        today = timezone.now().astimezone(tz)
        return self.filter(start__date=today.date())
    

    def start_date_gte(self, date: datetime.date):
        """
        Return all sessions whose start date is greater than or equal to the given date

        :param date: Date to filter from
        :param tz: Timezone to use for filtering
        """
        return self.filter(start__date__gte=date)



class SessionManager(BaseManager.from_queryset(SessionQuerySet)):
    """Custom manager for the Session model"""

    def get_queryset(self) -> SessionQuerySet:
        return super().get_queryset()
    

    def pending(self) -> SessionQuerySet:
        """Returns sessions that have not been held and have not been not cancelled"""
        return self.get_queryset().pending()
    

    def has_link(self) -> SessionQuerySet:
        """Returns only sessions with a link attached"""
        return self.get_queryset().has_link()
    

    def approved(self) -> SessionQuerySet:
        """Returns sessions that are pending and already have a session link attached"""
        return self.get_queryset().approved()
    

    def unapproved(self) -> SessionQuerySet:
        """Returns sessions that are pending and do not have a session link attached"""
        return self.get_queryset().unapproved()
    

    def missed(self, tz: Optional[timezone.tzinfo] = None) -> SessionQuerySet:
        """
        Returns sessions that were missed. That is, sessions that are still
        pending even after their end datetime.
        """
        return self.get_queryset().missed(tz=tz)
    

    def cancelled(self) -> SessionQuerySet:
        """Returns sessions that have been cancelled"""
        return self.get_queryset().cancelled()
    
    
    def today(self, tz: Optional[timezone.tzinfo] = None) -> SessionQuerySet:
        """
        Returns sessions that are scheduled for today

        :param tz: Timezone to use for filtering
        """
        return self.get_queryset().today(tz=tz)


    def start_date_gte(self, date: datetime.date) -> SessionQuerySet:
        """
        Return all sessions whose start date is greater than or equal to the given date

        :param date: Date to filter from
        :param tz: Timezone to use for filtering
        """
        return self.get_queryset().start_date_gte(date=date)

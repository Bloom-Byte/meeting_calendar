from typing import Optional
from django.db import models
from django.db.models.manager import BaseManager
from django.utils import timezone


class SessionQuerySet(models.QuerySet):
    """Custom queryset for the Session model"""

    def pending(self):
        """
        Returns sessions that have not been held and have not been not cancelled
        """
        return self.filter(has_held=False, cancelled=False)
    

    def missed(self, tz: Optional[timezone.tzinfo] = None):
        """
        Returns previously pending sessions that were missed. That is, sessions that 
        have not been held even after their end datetime.
        """
        return self.pending().filter(end__lte=timezone.now().astimezone(tz))
    

    def cancelled(self):
        """Returns sessions that have been cancelled"""
        return self.filter(cancelled=True)
    

    def today(self, tz: Optional[timezone.tzinfo] = None):
        """
        Filter sessions that are scheduled for today

        :param tz: Timezone to use for filtering
        """
        today = timezone.now().astimezone(tz)
        return self.filter(start__date=today.date())
    
    
    def has_link(self):
        """Returns only sessions with a link attached"""
        return self.exclude(link__isnull=True)



class SessionManager(BaseManager.from_queryset(SessionQuerySet)):
    """Custom manager for the Session model"""

    def get_queryset(self) -> SessionQuerySet:
        return super().get_queryset()
    

    def pending(self) -> SessionQuerySet:
        """Returns sessions that have not been held and have not been not cancelled"""
        return self.get_queryset().pending()
    

    def missed(self, tz: Optional[timezone.tzinfo] = None):
        """
        Returns sessions that were missed. That is, sessions that are still
        pending even after their end datetime.
        """
        return self.get_queryset().missed(tz=tz)
    

    def cancelled(self):
        """Returns sessions that have been cancelled"""
        return self.get_queryset().cancelled()
    
    
    def today(self, tz: Optional[timezone.tzinfo] = None) -> SessionQuerySet:
        """
        Filter sessions that are scheduled for today

        :param tz: Timezone to use for filtering
        """
        return self.get_queryset().today(tz=tz)


    def has_link(self) -> SessionQuerySet:
        """Returns only sessions with a link attached"""
        return self.get_queryset().has_link()


from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from typing import Any
from django.http import HttpRequest, HttpResponse, Http404
from django.shortcuts import redirect

from links.models import Link
from .models import Session
from helpers.response import response_message



class SessionLinkView(LoginRequiredMixin, generic.DetailView):
    """
    Performs necessary checks before redirecting to the internal (session) link's URL.
    """
    model = Link
    http_method_names = ["get"]
    slug_field = "identifier"
    slug_url_kwarg = "identifier"
    
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        try:
            link: Link = self.get_object()
        except Http404:
            return response_message(
                request,
                title="Invalid Link",
                content="This link is invalid or has expired. Please check the link and try again.",
                status=404
            )
        try:
            session = Session.objects.get(link=link)
        except Session.DoesNotExist:
            return response_message(
                request,
                title="Session Not Found",
                content="No session can be associated with this link.",
                status=404
            )
        else:
            if session.cancelled:
                return response_message(
                    request,
                    title="Session Cancelled",
                    content="This session has been cancelled.",
                    status=404
                )
            if session.was_missed(tz=request.user.utz):
                return response_message(
                    request,
                    title="Session Missed",
                    content="This session was missed. Please reschedule and try again.",
                    status=404
                )
        return redirect(link.url)



class SessionCalendarView(generic.TemplateView):
    template_name = 'booking/session_calendar.html'
    http_method_names = ["get"]



session_link_view = SessionLinkView.as_view()
session_calendar_view = SessionCalendarView.as_view()

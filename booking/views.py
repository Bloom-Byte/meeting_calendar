from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views import generic
from typing import Any, Dict
import json
from django.http import HttpRequest, HttpResponse, Http404, JsonResponse
from django.shortcuts import redirect

from links.models import Link
from .models import Session
from .forms import SessionForm
from helpers.response import response_message
from .utils import (
    get_unavailable_times_for_date, get_bookings_by_user_on_date,
    remove_booked_time_periods_from_unavailable_times
)



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
        
        # Check if the link can be associated with a session
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
            # Check if the session is cancelled or missed
            if session.cancelled:
                return response_message(
                    request,
                    title="Session Cancelled",
                    content="This session has been cancelled.",
                    status=400
                )
            if session.was_missed(tz=request.user.utz):
                return response_message(
                    request,
                    title="Session Missed",
                    content="This session was missed. Please reschedule and try again.",
                    status=400
                )
            
            # Check if the session has not ended. If it has, it should not be accessible
            # Link becomes inactive 5 minutes after the session ends
            now = timezone.now().astimezone(request.user.utz)
            end_plus_5mins = session.end + timezone.timedelta(minutes=5)
            if now > end_plus_5mins:
                return response_message(
                    request,
                    title="Session Ended",
                    content="This link is no longer valid. The session has ended.",
                    status=400
                )
            
            # Check if the session has not started. If it has, it should not be accessible
            # Link becomes active 5 minutes before the session starts
            start_minus_5mins = session.start - timezone.timedelta(minutes=5)
            if now < start_minus_5mins:
                return response_message(
                    request,
                    title="Session Not Started",
                    content="This link is not yet active. The session has not started.",
                    status=400
                )
        return redirect(link.url)



class SessionCalendarView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'booking/session_calendar.html'
    http_method_names = ["get", "post"]

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> JsonResponse:
        data: Dict = json.loads(request.body)
        date: str = data.get('date', None)

        if not date:
            return JsonResponse(
                data={
                    "status": "error",
                    "detail": "Date is required."
                },
                status=400
            )
        try:
            unavailable_times = get_unavailable_times_for_date(date, tz=request.user.utz)
            bookings = get_bookings_by_user_on_date(date, user=request.user)
            remove_booked_time_periods_from_unavailable_times(bookings, unavailable_times)
        except Exception:
            return JsonResponse(
                data={
                    "status": "error",
                    "detail": "An error occurred. Please try again."
                },
                status=500
            )
        return JsonResponse(
            data={
                "status": "success",
                "detail": "Unavailable times for the given date fetched successfully.",
                "data": {
                    "unavailable_times": unavailable_times,
                    "bookings": bookings
                }
            },
            status=200
        )



class SessionBookingView(generic.View):
    model = Session
    form_class = SessionForm
    http_method_names = ["post"]

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> JsonResponse:
        data: Dict = json.loads(request.body)
        data["booked_by"] = request.user
        data["timezone"] = request.user.utz
        session_form = self.form_class(data=data)

        if session_form.is_valid():
            session = session_form.save(commit=False)
            session.save()
            return JsonResponse(
                data={
                    "status": "success",
                    "detail": "Session booked successfully.",
                    "data": {
                        "session_id": session.id
                    }
                },
                status=201
            )
        return JsonResponse(
            data={
                "status": "error",
                "detail": "An error occurred. Please try again.",
                "errors": session_form.errors
            },
            status=400
        )



class SessionUpdateView(generic.UpdateView):
    model = Session
    form_class = SessionForm
    http_method_names = ["post"]

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> JsonResponse:
        data: Dict = json.loads(request.body)
        session_id = data.pop('session-id', None)

        if not session_id:
            return JsonResponse(
                data={
                    "status": "error",
                    "detail": "Session ID is required."
                },
                status=400
            )
        try:
            session = Session.objects.get(id=session_id)
        except Session.DoesNotExist:
            return JsonResponse(
                data={
                    "status": "error",
                    "detail": "Session not found."
                },
                status=404
            )
        if session.booked_by != request.user:
            return JsonResponse(
                data={
                    "status": "error",
                    "detail": "You are not authorized to perform this action."
                },
                status=403
            )
        
        data["booked_by"] = request.user
        session_form = self.form_class(data=data, instance=session)

        if session_form.is_valid():
            session: Session = session_form.save(commit=False)
            session.save()
            return JsonResponse(
                data={
                    "status": "success",
                    "detail": "Session updated successfully.",
                    "data": {
                        "session_id": session.id
                    }
                },
                status=200
            )
        return JsonResponse(
            data={
                "status": "error",
                "detail": "An error occurred. Please try again.",
                "errors": session_form.errors
            },
            status=400
        )



session_link_view = SessionLinkView.as_view()
session_calendar_view = SessionCalendarView.as_view()
session_booking_view = SessionBookingView.as_view()
session_update_view = SessionUpdateView.as_view()


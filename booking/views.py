from django.views import generic


class SessionCalendarView(generic.TemplateView):
    template_name = 'booking/session_calendar.html'
    http_method_names = ["get"]



session_calendar_view = SessionCalendarView.as_view()

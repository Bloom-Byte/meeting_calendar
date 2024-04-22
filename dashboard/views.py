from typing import Any
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

from booking.models import Session
from news.models import News
from .utils import get_todays_sessions_for_user, get_todays_news_for_user

session_qs = Session.objects.select_related('booked_by').all().order_by("start")
news_qs = News.objects.all()


class DashboardView(LoginRequiredMixin, generic.TemplateView):
    """View for the user dashboard."""
    template_name = "dashboard/dashboard.html"
    http_method_names = ["get"]

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["todays_sessions"] = get_todays_sessions_for_user(session_qs, user)
        context["todays_news"] = get_todays_news_for_user(news_qs, user)
        return context


dashboard_view = DashboardView.as_view()

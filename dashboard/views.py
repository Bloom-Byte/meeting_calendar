from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin



class DashboardView(LoginRequiredMixin, generic.TemplateView):
    """View for the user dashboard."""
    template_name = "dashboard/dashboard.html"
    http_method_names = ["get"]


dashboard_view = DashboardView.as_view()

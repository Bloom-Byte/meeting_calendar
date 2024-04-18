from django.urls import path

from . import views


app_name = "booking"

urlpatterns = [
    path("calendar/", views.session_calendar_view, name="session_calendar"),
]

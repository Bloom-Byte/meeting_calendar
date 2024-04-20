from django.contrib import admin

from .models import Session, UnavailablePeriod
from .forms import SessionForm, UnavailablePeriodForm


@admin.register(Session)
class SessionModelAdmin(admin.ModelAdmin):
    """Model admin for the Session model"""
    form = SessionForm
    list_display = [
        "title", "start", "end", "booked_by", 
        "link", "is_pending", "cancelled",
        "created_at", "updated_at"
    ]
    search_fields = ["title", "booked_by__email"]



@admin.register(UnavailablePeriod)
class UnavailablePeriodModelAdmin(admin.ModelAdmin):
    """Model admin for the UnavailablePeriod model"""
    form = UnavailablePeriodForm
    list_display = ["start", "end", "created_at", "updated_at"]
    search_fields = ["start__date", "end__date", "start__time", "end__time"]

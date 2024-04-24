from django.conf import settings
from typing import Any
from django.contrib import admin
from django.http import HttpRequest
from django_utz.middleware import get_request_user

from .models import Session, UnavailablePeriod
from .forms import SessionForm, UnavailablePeriodAdminForm



@admin.register(Session)
class SessionModelAdmin(admin.ModelAdmin):
    """Model admin for the Session model"""
    form = SessionForm
    list_display = [
        "title", "starts", "ends", "booked_by", 
        "link", "has_held", "cancelled", "booked_at",
        "rescheduled"
    ]
    search_fields = ["title", "booked_by__email", "booked_by__firstname", "booked_by__lastname"]
    readonly_fields = ["booked_by", "rescheduled_at"]
    date_hierarchy = "start"
    ordering = ["-start__date", "start__time"]

    def save_model(self, request: Any, obj: Any, form: Any, change: Any) -> None:
        # Set the booked_by field to the request user
        form.instance.booked_by = request.user
        return super().save_model(request, obj, form, change)

    def has_add_permission(self, request: HttpRequest) -> bool:
        # Only allow sessions to be created from admin during development
        if settings.DEBUG:
            return True
        return False
    
    def starts(self, obj: Session) -> Any:
        """Start time in the request user's timezone"""
        request_user = get_request_user()
        return request_user.to_local_timezone(obj.start)
    
    def ends(self, obj: Session) -> Any:
        """End time in the request user's timezone"""
        request_user = get_request_user()
        return request_user.to_local_timezone(obj.end)
    
    def booked_at(self, obj: Session) -> Any:
        """Created time in the request user's timezone"""
        request_user = get_request_user()
        return request_user.to_local_timezone(obj.created_at)
    
    def rescheduled(self, obj: Session) -> Any:
        """Updated time in the request user's timezone"""
        request_user = get_request_user()
        if not obj.rescheduled_at:
            return None
        return request_user.to_local_timezone(obj.rescheduled_at)
    
    


@admin.register(UnavailablePeriod)
class UnavailablePeriodModelAdmin(admin.ModelAdmin):
    """Model admin for the UnavailablePeriod model"""
    form = UnavailablePeriodAdminForm
    list_display = ["start", "till", "created", "updated"]
    search_fields = ["start__date", "end__date", "start__time", "end__time"]
    date_hierarchy = "start"
    ordering = ["-start"]

    def has_add_permission(self, request: HttpRequest) -> bool:
        return request.user.is_staff

    def starts(self, obj: Session) -> Any:
        """Start time in the request user's timezone"""
        request_user = get_request_user()
        return request_user.to_local_timezone(obj.start)
    
    def till(self, obj: Session) -> Any:
        """End time in the request user's timezone"""
        request_user = get_request_user()
        return request_user.to_local_timezone(obj.end)
    
    def created(self, obj: Session) -> Any:
        """Created time in the request user's timezone"""
        request_user = get_request_user()
        return request_user.to_local_timezone(obj.created_at)
    
    def updated(self, obj: Session) -> Any:
        """Updated time in the request user's timezone"""
        request_user = get_request_user()
        return request_user.to_local_timezone(obj.updated_at)

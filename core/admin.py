from django.contrib import admin
from django.contrib.auth.models import Group
from rest_framework_api_key.models import APIKey
import datetime
from django.http import HttpRequest
from typing import Optional

from .models import BusinessHoursSettings
from .forms import BusinessHoursSettingsForm


admin.site.unregister(APIKey)
admin.site.unregister(Group)


@admin.register(BusinessHoursSettings)
class BusinessHoursSettingsModelAdmin(admin.ModelAdmin):
    form = BusinessHoursSettingsForm
    readonly_fields = ["created_at", "updated_at"]
    list_display = ["opens_at", "closes_at", "timezone", "created", "updated"]

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False
    
    def has_change_permission(self, request: HttpRequest, obj: Optional[BusinessHoursSettingsForm] = None) -> bool:
        return request.user.is_superuser
    
    def has_delete_permission(self, request: HttpRequest, obj: Optional[BusinessHoursSettingsForm] = None) -> bool:
        return False

    def created(self, obj: BusinessHoursSettings) -> datetime.datetime:
        """Created time in the request user's timezone"""
        return obj.created_at_user_tz

    
    def updated(self, obj: BusinessHoursSettings) -> datetime.datetime:
        """Updated time in the request user's timezone"""
        return obj.updated_at_user_tz

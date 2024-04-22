from django.contrib import admin
from typing import Any
from django.http import HttpRequest
from django_utz.middleware import get_request_user

from .models import Link
from .forms import LinkForm


@admin.register(Link)
class LinkModelAdmin(admin.ModelAdmin):
    """Model admin for the Link model"""
    form = LinkForm
    readonly_fields = ["identifier", "created_at", "updated_at"]
    search_fields = ["created_by__email", "created_by__firstname", "created_by__lastname", "identifier"]
    list_display = ["identifier", "created_by", "created", "updated"]

    # Links should only be created by sessions
    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def created(self, obj: Link) -> Any:
        """Created time in the request user's timezone"""
        request_user = get_request_user()
        return request_user.to_local_timezone(obj.created_at)
    
    def updated(self, obj: Link) -> Any:
        """Updated time in the request user's timezone"""
        request_user = get_request_user()
        return request_user.to_local_timezone(obj.updated_at)

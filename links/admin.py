from django.contrib import admin
import datetime
from django.http import HttpRequest

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

    def created(self, obj: Link) -> datetime.datetime:
        """Created time in the request user's timezone"""
        return obj.created_at_user_tz
    
    def updated(self, obj: Link) -> datetime.datetime:
        """Updated time in the request user's timezone"""
        return obj.updated_at_user_tz

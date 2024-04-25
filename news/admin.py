from django.contrib import admin
from typing import Any

from .models import News
from .forms import NewsForm


@admin.register(News)
class NewsModelAdmin(admin.ModelAdmin):
    """Model admin for the News model"""
    form = NewsForm
    list_display = ["headline", "author", "created", "updated"]
    readonly_fields = ["created_at", "updated_at", "author"]
    search_fields = ["headline", "author__email", "author__firstname", "author__lastname"]
    date_hierarchy = "created_at"

    def has_add_permission(self, request) -> bool:
        return request.user.is_staff

    def has_change_permission(self, request, obj=None) -> bool:
        return request.user.is_staff

    def has_delete_permission(self, request, obj=None) -> bool:
        return request.user.is_staff
    
    def save_model(self, request, obj, form, change) -> None:
        obj.author = request.user
        obj.save()
        return None
    
    def created(self, obj: News) -> Any:
        """Created time in the request user's timezone"""
        return obj.created_at_user_tz
    
    def updated(self, obj: News) -> Any:
        """Updated time in the request user's timezone"""
        return obj.updated_at_user_tz

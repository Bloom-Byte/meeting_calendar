from django.contrib import admin
from typing import Any
from django_utz.middleware import get_request_user

from .models import News



@admin.register(News)
class NewsModelAdmin(admin.ModelAdmin):
    """Model admin for the News model"""
    list_display = ["headline", "author", "created", "updated"]
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
        request_user = get_request_user()
        return request_user.to_local_timezone(obj.created_at)
    
    def updated(self, obj: News) -> Any:
        """Updated time in the request user's timezone"""
        request_user = get_request_user()
        return request_user.to_local_timezone(obj.updated_at)

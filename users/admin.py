from django.contrib import admin
from typing import Any
from django_utz.middleware import get_request_user

from .models import UserAccount
from .forms import UserForm


@admin.register(UserAccount)
class UserAccountModelAdmin(admin.ModelAdmin):
    """Custom UserAccount model admin."""
    form = UserForm
    readonly_fields = ["slug", "last_login"]
    list_display = [
        "email", "firstname", "lastname", "timezone", 
        "is_active", "is_staff", "is_admin", "registered", "updated"
    ]
    search_fields = ["email", "firstname", "lastname", "timezone"]

    def save_model(self, request, obj, form, change):
        # If password is set, then set it using the set_password method
        if "password" in form.changed_data:
            obj.set_password(form.cleaned_data["password"])
        obj.save()
        return None
    
    def has_add_permission(self, request):
        return request.user.is_admin
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_admin
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_admin
    
    def registered(self, obj: UserAccount) -> Any:
        """Registered time in the request user's timezone"""
        request_user = get_request_user()
        return request_user.to_local_timezone(obj.registered_at)
    
    def updated(self, obj: UserAccount) -> Any:
        """Updated time in the request user's timezone"""
        request_user = get_request_user()
        return request_user.to_local_timezone(obj.updated_at)


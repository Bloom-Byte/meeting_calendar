from django.contrib import admin
from django.http import HttpRequest

from .models import PasswordResetToken


@admin.register(PasswordResetToken)
class PasswordResetTokenModelAdmin(admin.ModelAdmin):
    """Model admin for the PasswordResetToken model"""
    list_display = ["name", "expiry_date"]
    search_fields = ["user__email", "user__firstname", "user__lastname", "expiry_date"]

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False
    
    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        return False
    
    


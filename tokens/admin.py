from django.contrib import admin
from django.http import HttpRequest

from .models import PasswordResetToken
from .forms import PasswordResetTokenForm


@admin.register(PasswordResetToken)
class PasswordResetTokenModelAdmin(admin.ModelAdmin):
    """Model admin for the PasswordResetToken model"""
    form = PasswordResetTokenForm
    list_display = ["name", "expires"]
    search_fields = ["user__email", "user__firstname", "user__lastname", "expiry_date"]

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False
    
    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        return False
    
    def expires(self, obj: PasswordResetToken) -> str:
        """Return expiry date in the user's timezone"""
        return obj.expiry_date_user_tz
    
    


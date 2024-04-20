from django.contrib import admin

from .models import Link
from .forms import LinkForm


@admin.register(Link)
class LinkModelAdmin(admin.ModelAdmin):
    """Model admin for the Link model"""
    form = LinkForm
    search_fields = ["url"]
    list_display = ["identifier", "created_at", "updated_at"]


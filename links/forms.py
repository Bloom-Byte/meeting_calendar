from django import forms
from django_utz.middleware import get_request_user

from . import models



class LinkForm(forms.ModelForm):
    """Custom model form for Link Model"""

    class Meta:
        model = models.Link
        fields = ["url"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            try:
                self.initial["created_at"] = self.instance.created_at_user_tz
                self.initial["updated_at"] = self.instance.updated_at_user_tz
            except (AttributeError, TypeError):
                pass
    
    def save(self, commit: bool = True) -> models.Link:
        instance = super().save(commit=False)
        request_user = get_request_user()
        if request_user and request_user.is_authenticated:
            instance.created_by = request_user
        else:
            self.add_error(error="Request user must be authenticated!")
        if commit:
            instance.save()
        return instance

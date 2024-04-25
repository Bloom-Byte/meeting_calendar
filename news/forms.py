from django import forms
from django_utz.middleware import get_request_user

from .models import News


class NewsForm(forms.ModelForm):
    """Form to create news"""
    class Meta:
        model = News
        fields = ["headline", "content", "display_at", "author"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request_user = get_request_user()
        if self.instance.pk:
            try:
                self.initial["display_at"] = request_user.to_local_timezone(self.instance.display_at)
                self.initial["created_at"] = request_user.to_local_timezone(self.instance.created_at)
                self.initial["updated_at"] = request_user.to_local_timezone(self.instance.updated_at)
            except (AttributeError, TypeError):
                pass
            

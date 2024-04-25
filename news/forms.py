from django import forms

from .models import News


class NewsForm(forms.ModelForm):
    """Form to create news"""
    class Meta:
        model = News
        fields = ["headline", "content", "display_at", "author"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            try:
                self.initial["display_at"] = self.instance.display_at_user_tz
                self.initial["created_at"] = self.instance.created_at_user_tz
                self.initial["updated_at"] = self.instance.updated_at_user_tz
            except (AttributeError, TypeError):
                pass
            

from django import forms

from . import models



class BusinessHoursSettingsForm(forms.ModelForm):
    """Custom model form for BusinessHoursSettings Model"""

    class Meta:
        model = models.BusinessHoursSettings
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            try:
                self.initial["created_at"] = self.instance.created_at_user_tz
                self.initial["updated_at"] = self.instance.updated_at_user_tz
            except (AttributeError, TypeError):
                pass
    
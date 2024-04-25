from django import forms

from .models import PasswordResetToken



class PasswordResetTokenForm(forms.ModelForm):

    class Meta:
        model = PasswordResetToken
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            try:
                self.initial["expires_at"] = self.instance.expiry_date_user_tz
            except (AttributeError, ValueError):
                pass

    

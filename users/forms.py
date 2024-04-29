# from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms

from .models import UserAccount


class UserForm(forms.ModelForm):
    """Form for creating a new user."""
    class Meta:
        model = UserAccount
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            try:
                self.initial["registered_at"] = self.instance.registered_at_user_tz
                self.initial["updated_at"] = self.instance.updated_at_user_tz
                self.initial["last_login"] = self.instance.last_login_user_tz
            except (AttributeError, TypeError):
                pass



class UserCreationForm(UserCreationForm):
    """Form for creating a new user."""
    class Meta(UserCreationForm.Meta):
        model = UserAccount
        fields = (
            "name", "email", "timezone", "password1", "password2"
        )



class UserUpdateForm(UserChangeForm):
    """Form for updating a user's detail"""
    class Meta(UserChangeForm.Meta):
        model = UserAccount
        fields = (
            "name", "email", "timezone"
        )

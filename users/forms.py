# from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from django_utz.middleware import get_request_user

from .models import UserAccount


class UserForm(forms.ModelForm):
    """Form for creating a new user."""
    class Meta:
        model = UserAccount
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request_user = get_request_user()
        try:
            registered_at_in_user_tz = request_user.to_local_timezone(self.instance.registered_at)
            updated_at_in_user_tz = request_user.to_local_timezone(self.instance.updated_at)
            last_login_in_user_tz = request_user.to_local_timezone(self.instance.last_login)
            self.initial["registered_at"] = registered_at_in_user_tz
            self.initial["updated_at"] = updated_at_in_user_tz
            self.initial["last_login"] = last_login_in_user_tz
        except (AttributeError, TypeError):
            pass



class UserCreationForm(UserCreationForm):
    """Form for creating a new user."""
    class Meta(UserCreationForm.Meta):
        model = UserAccount
        fields = (
            "firstname", "lastname", "email", 
            "timezone", "password1", "password2",
        )



class UserUpdateForm(UserChangeForm):
    """Form for updating a user's detail"""
    class Meta(UserChangeForm.Meta):
        model = UserAccount
        fields = (
            "firstname", "lastname", "email", 
            "timezone",
        )

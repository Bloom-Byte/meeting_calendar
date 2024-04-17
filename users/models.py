from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
import uuid
from typing import Any
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django_utz.decorators import model, usermodel
from timezone_field import TimeZoneField
from django.core.mail import EmailMessage, get_connection as get_smtp_connection

from .managers import UserAccountManager


@model
@usermodel
class UserAccount(PermissionsMixin, AbstractBaseUser):
    """Custom user model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    email = models.EmailField(_("email address"), unique=True)
    slug = models.SlugField(max_length=255, unique=True)
    timezone = TimeZoneField(_("timezone"), default="UTC", help_text=_("Choose your timezone."))
    is_active = models.BooleanField(_("active") ,default=True)
    is_admin = models.BooleanField(_("admin") ,default=False)
    is_staff = models.BooleanField(_("staff") ,default=False)
    is_superuser = models.BooleanField(_("superuser") ,default=False)
    registered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ("firstname", "lastname")

    objects = UserAccountManager()

    class Meta:
        verbose_name = _("user account")
        verbose_name_plural = _("user accounts")
    
    class UTZMeta:
        timezone_field = "timezone"
        datetime_fields = "__all__"
    

    def __str__(self) -> str:
        return self.email
    
    @property
    def fullname(self):
        return f"{self.firstname} {self.lastname}"
    
    @property
    def initials(self):
        return f"{self.firstname[0]}{self.lastname[0]}"
    

    def save(self, *args: Any, **kwargs: Any) -> None:
        try:
            old_instance = UserAccount.objects.get(pk=self.pk)
        except UserAccount.DoesNotExist:
            old_instance = None
        
        name_changed = old_instance and old_instance.fullname != self.fullname
        if not self.slug or name_changed:
            slug = slugify(self.fullname) + "-" + str(uuid.uuid4())[:8]
            self.slug = slug
        super().save(*args, **kwargs)
        return None
    

    def send_mail(
            self, 
            subject: str, 
            message: str, 
            from_email: str = settings.DEFAULT_FROM_EMAIL, 
            connection: Any | None = None,
            html: bool = False
        ) -> None:
        """
        Send email to user.
        
        :param subject: The subject of the email.
        :param message: The message to send.
        :param from_email: The email address to send from.
        :param connection: The email connection to use.
        :param html: Whether the message is an html message.
        """
        connection = connection or get_smtp_connection()
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=f"{settings.SITE_NAME} <{from_email}>",
            to=[self.email],
            connection=connection
        )
        if html:
            email.content_subtype = "html"
        email.send(fail_silently=False)
        return None

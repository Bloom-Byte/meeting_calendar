from django.contrib import admin
from django.contrib.auth.models import Group
from rest_framework_api_key.models import APIKey

admin.site.unregister(APIKey)
admin.site.unregister(Group)


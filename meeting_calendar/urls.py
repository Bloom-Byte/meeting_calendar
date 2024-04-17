from django.contrib import admin
from django.urls import path, include
from django.conf import settings


urlpatterns = [
    path('dashboard/', include('dashboard.urls', namespace="dashboard")),
    path('admin/', admin.site.urls),
    path('accounts/', include('users.urls', namespace="users")),
]


admin.site.site_header = f"{settings.SITE_NAME or "Django"} Admin"
admin.site.site_title = f"{settings.SITE_NAME or "Django"} Admin"
admin.site.index_title = f"{settings.SITE_NAME or "Django"} Admin"

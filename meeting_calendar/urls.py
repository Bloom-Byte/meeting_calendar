from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("", include('core.urls', namespace="core")),
    path('dashboard/', include('dashboard.urls', namespace="dashboard")),
    path('admin/', admin.site.urls),
    path('accounts/', include('users.urls', namespace="users")),
    path('booking/', include('booking.urls', namespace="booking")),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


admin.site.site_header = f"{settings.SITE_NAME or 'Django'} Admin"
admin.site.site_title = f"{settings.SITE_NAME or 'Django'} Admin"
admin.site.index_title = f"{settings.SITE_NAME or 'Django'} Admin"

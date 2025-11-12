
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    # Password reset flow (Django built-ins)
    path('password-reset/', core_views.password_reset_request, name='password_reset'),
    path('password-reset/done/', core_views.password_reset_done_view, name='password_reset_done'),
    path('reset/<uidb64>/<token>/', core_views.password_reset_confirm_view, name='password_reset_confirm'),
    path('reset/done/', core_views.password_reset_complete_view, name='password_reset_complete'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

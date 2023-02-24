from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

from manager.views import ControlPanel


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', view=ControlPanel.as_view(), name="control_panel"),
    path('api/', include('manager.urls', namespace='manager'), name='manager')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

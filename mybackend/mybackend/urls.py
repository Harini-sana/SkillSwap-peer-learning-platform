from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", lambda request: HttpResponse("SkillSwap backend running ✅")),

    path("admin/", admin.site.urls),

    # API routes
    path("api/", include("api.urls")),

    # Progress app routes (NOT under /api/)
    path("progress/", include("progress.urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

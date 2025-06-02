from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("authentication.urls")),
    path("api/meetings/", include("meetings.urls")),
    path("api/recordings/", include("recordings.urls")),
    path("api/transcriptions/", include("transcriptions.urls")),
    path("api/ai/", include("ai_features.urls")),
    path("api/files/", include("file_management.urls")),
]

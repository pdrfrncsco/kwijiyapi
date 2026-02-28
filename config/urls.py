"""
URL configuration for Kwijiya API.
All API endpoints are versioned under /api/v1/.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),

    # API v1
    path('api/v1/auth/', include('users.urls')),
    path('api/v1/languages/', include('languages.urls')),
    path('api/v1/quizzes/', include('quizzes.urls')),
    path('api/v1/gamification/', include('gamification.urls')),
    path('api/v1/progress/', include('progress.urls')),
    path('api/v1/rankings/', include('rankings.urls')),
    path('api/v1/users/', include('users.profile_urls')),

    # Swagger / API Docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

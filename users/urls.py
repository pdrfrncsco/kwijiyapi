"""Auth URLs — /api/v1/auth/"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('request-otp/', views.request_otp, name='request-otp'),
    path('verify-otp/', views.verify_otp, name='verify-otp'),
    path('guest/', views.guest_login, name='guest-login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('xp-log/', views.UserXPLogListView.as_view(), name='xp-log'),
    path('badges/', views.BadgeListView.as_view(), name='badge-list'),
]

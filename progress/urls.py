from django.urls import path
from . import views

urlpatterns = [
    path('', views.UserProgressListView.as_view(), name='progress-list'),
    path('stats/', views.user_stats, name='user-stats'),
]

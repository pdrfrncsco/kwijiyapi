from django.urls import path
from . import views

urlpatterns = [
    path('global/', views.global_ranking, name='global-ranking'),
    path('weekly/', views.weekly_ranking, name='weekly-ranking'),
]

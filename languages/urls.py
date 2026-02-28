from django.urls import path
from . import views

urlpatterns = [
    path('', views.LanguageListView.as_view(), name='language-list'),
]

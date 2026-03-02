from django.urls import path
from . import views

urlpatterns = [
    path('start/', views.start_quiz, name='start-quiz'),
    path('submit/', views.submit_answer, name='submit-answer'),
    path('session/<uuid:pk>/', views.QuizSessionDetailView.as_view(), name='session-detail'),
    path('placement/start/', views.start_placement_test, name='start-placement'),
    path('placement/submit/', views.submit_placement_test, name='submit-placement'),
]

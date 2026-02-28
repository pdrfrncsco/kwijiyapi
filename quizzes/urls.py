from django.urls import path
from . import views

urlpatterns = [
    path('start/', views.start_quiz, name='start-quiz'),
    path('submit/', views.submit_answer, name='submit-answer'),
    path('session/<uuid:pk>/', views.QuizSessionDetailView.as_view(), name='session-detail'),
]

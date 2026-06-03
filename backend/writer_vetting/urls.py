from django.urls import path
from . import views

app_name = "writer_vetting"

urlpatterns = [
    path("quizzes/",                           views.QuizListView.as_view(),       name="quiz-list"),
    path("quizzes/<int:pk>/",                  views.QuizDetailView.as_view(),     name="quiz-detail"),
    path("quizzes/<int:quiz_pk>/questions/",   views.QuestionListView.as_view(),   name="question-list"),
    path("questions/<int:pk>/",                views.QuestionDetailView.as_view(), name="question-detail"),
    path("choices/<int:pk>/",                  views.ChoiceDetailView.as_view(),   name="choice-detail"),
]

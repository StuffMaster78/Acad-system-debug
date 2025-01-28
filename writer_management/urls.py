from django.urls import path
from . import views

urlpatterns = [
    path('profile/<int:pk>/', views.WriterProfileDetailView.as_view(), name='writer-profile-detail'),
    path('leaves/', views.WriterLeaveListCreateView.as_view(), name='writer-leave-list-create'),
    path('actions/', views.WriterActionLogListView.as_view(), name='writer-action-log-list'),
    path('education/', views.WriterEducationListCreateView.as_view(), name='writer-education-list-create'),
    path('payments/', views.PaymentHistoryListView.as_view(), name='payment-history-list'),
    path('rewards/', views.WriterRewardListCreateView.as_view(), name='writer-reward-list-create'),
    path('ratings/', views.WriterRatingListView.as_view(), name='writer-rating-list'),
]

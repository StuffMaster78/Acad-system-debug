from django.urls import path
from .views import (
    WriterLevelListView,
    PaymentHistoryListView,
    WriterProgressListView,
    WriterAvailabilityListView,
    WriterPerformanceDetailView,
    WriterOrderAssignmentListView,
    WriterReviewListView,
)

urlpatterns = [
    # List all writer levels
    path('levels/', WriterLevelListView.as_view(), name='writer-levels'),
    
    # List payment history for the authenticated writer
    path('payment-history/', PaymentHistoryListView.as_view(), name='payment-history'),
    
    # List progress updates for the authenticated writer
    path('progress/', WriterProgressListView.as_view(), name='writer-progress'),

    # List and create availability schedules for the authenticated writer
    path('availability/', WriterAvailabilityListView.as_view(), name='writer-availability'),

    # Retrieve performance details for the authenticated writer
    path('performance/', WriterPerformanceDetailView.as_view(), name='writer-performance'),

    # List assignments for the authenticated writer
    path('assignments/', WriterOrderAssignmentListView.as_view(), name='writer-assignments'),

    # List reviews for the authenticated writer
    path('reviews/', WriterReviewListView.as_view(), name='writer-reviews'),
]
from django.urls import path
from .views import QAResultView, QATemplateListView

urlpatterns = [
    path("templates/", QATemplateListView.as_view(), name="qa-templates"),
    path("orders/<int:order_id>/results/", QAResultView.as_view(), name="qa-results"),
]

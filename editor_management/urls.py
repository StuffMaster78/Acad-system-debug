from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'profiles', views.EditorProfileViewSet, basename='editor-profile')
router.register(r'tasks', views.EditorTaskAssignmentViewSet, basename='editor-task')
router.register(r'reviews', views.EditorReviewSubmissionViewSet, basename='editor-review')
router.register(r'notifications', views.EditorNotificationsViewSet, basename='editor-notification')
router.register(r'performance', views.EditorPerformanceViewSet, basename='editor-performance')
router.register(r'admin-assignments', views.AdminEditorAssignmentViewSet, basename='admin-editor-assignment')

urlpatterns = [
    path('', include(router.urls)),
]

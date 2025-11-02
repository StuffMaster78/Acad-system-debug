from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PaperTypeViewSet,
    FormattingStyleViewSet,
    SubjectViewSet,
    TypeOfWorkViewSet,
    EnglishTypeViewSet,
    WriterDeadlineConfigViewSet,
    RevisionPolicyConfigViewSet,
    EditingRequirementConfigViewSet
)

router = DefaultRouter()
router.register(
    'paper-types',
    PaperTypeViewSet,
    basename='paper-type'
)
router.register(
    'formatting-styles',
    FormattingStyleViewSet,
    basename='formatting-style'
)
router.register(
    'subjects',
    SubjectViewSet,
    basename='subject'
)
router.register(
    'types-of-work',
    TypeOfWorkViewSet,
    basename='type-of-work'
)
router.register(
    'english-types',
    EnglishTypeViewSet,
    basename='english-type'
)
router.register(
    'writer-deadline-configs',
    WriterDeadlineConfigViewSet,
    basename='writer-deadline-config'
)
router.register(
    r'revision-policy',
    RevisionPolicyConfigViewSet,
    basename='revision-policy'
)
router.register(
    r'editing-requirements',
    EditingRequirementConfigViewSet,
    basename='editing-requirement-config'
)

urlpatterns = [
    path('api/', include(router.urls)),
]
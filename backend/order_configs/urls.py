from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AcademicLevelViewSet,
    PaperTypeViewSet,
    FormattingStyleViewSet,
    SubjectViewSet,
    TypeOfWorkViewSet,
    EnglishTypeViewSet,
    WriterDeadlineConfigViewSet,
    RevisionPolicyConfigViewSet,
    EditingRequirementConfigViewSet,
    OrderConfigManagementViewSet,
    SubjectTemplateViewSet,
    PaperTypeTemplateViewSet,
    TypeOfWorkTemplateViewSet,
)

router = DefaultRouter()
router.register(
    'academic-levels',
    AcademicLevelViewSet,
    basename='academic-level'
)
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
router.register(
    r'management',
    OrderConfigManagementViewSet,
    basename='order-config-management'
)
router.register(
    r'subject-templates',
    SubjectTemplateViewSet,
    basename='subject-template'
)
router.register(
    r'paper-type-templates',
    PaperTypeTemplateViewSet,
    basename='paper-type-template'
)
router.register(
    r'type-of-work-templates',
    TypeOfWorkTemplateViewSet,
    basename='type-of-work-template'
)

urlpatterns = [
    path('api/', include(router.urls)),
]
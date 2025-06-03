from rest_framework.routers import DefaultRouter
from fines.views import FineActionViewSet, FineAppealActionViewSet

router = DefaultRouter()
router.register("fines/actions", FineActionViewSet, basename="fine-actions")
router.register("fine-appeals/actions", FineAppealActionViewSet, basename="fine-appeal-actions")

urlpatterns = router.urls
from rest_framework.routers import DefaultRouter

from .views import MediaAssetViewSet, MediaUsageViewSet

router = DefaultRouter()
router.register(r"media-assets", MediaAssetViewSet, basename="media-assets")
router.register(r"media-usages", MediaUsageViewSet, basename="media-usages")

urlpatterns = router.urls



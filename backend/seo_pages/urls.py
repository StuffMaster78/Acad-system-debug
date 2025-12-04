"""
URL routing for SEO Pages.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SeoPageViewSet, PublicSeoPageViewSet

router = DefaultRouter()
router.register(r'seo-pages', SeoPageViewSet, basename='seo-page')

urlpatterns = [
    path('', include(router.urls)),
    # Public endpoint
    path('public/seo-pages/', PublicSeoPageViewSet.as_view({'get': 'list'}), name='public-seo-pages-list'),
    path('public/seo-pages/<slug:slug>/', PublicSeoPageViewSet.as_view({'get': 'retrieve'}), name='public-seo-page-detail'),
]


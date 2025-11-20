"""
URLs for core app - dropdown options and other shared endpoints.
"""
from django.urls import path
from core.views.dropdown_options import DropdownOptionsView, DropdownOptionsByCategoryView

urlpatterns = [
    path('', DropdownOptionsView.as_view(), name='dropdown-options'),
    path('<str:category>/', DropdownOptionsByCategoryView.as_view(), name='dropdown-options-category'),
]


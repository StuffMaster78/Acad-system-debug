from django.urls import path, include
from rest_framework.routers import DefaultRouter
# Import views directly from views.py file (not from views/ package)
# We need to import it as a regular module to allow relative imports to work
import sys
import importlib.util
from pathlib import Path

# Get the views.py file path
_views_py_path = Path(__file__).parent / 'views.py'
_parent_dir = str(Path(__file__).parent.parent)  # Go up to writing_project/backend level

# Add parent directory to path to allow proper imports
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

try:
    # Import the views module with proper package context
    # This allows relative imports (from .permissions import ...) to work
    spec = importlib.util.spec_from_file_location("client_management.views", str(_views_py_path))
    views_module = importlib.util.module_from_spec(spec)
    
    # Set up proper package context for relative imports
    views_module.__package__ = 'client_management'
    views_module.__name__ = 'client_management.views'
    views_module.__file__ = str(_views_py_path)
    
    # Register the parent package in sys.modules if not already there
    if 'client_management' not in sys.modules:
        import types
        client_management_pkg = types.ModuleType('client_management')
        client_management_pkg.__path__ = [str(Path(__file__).parent)]
        sys.modules['client_management'] = client_management_pkg
    
    # Now execute the module - relative imports should work now
    spec.loader.exec_module(views_module)
    
    # Extract all the views we need
    views = views_module  # Use as 'views' for consistency with existing code
    BlacklistEmailListView = views_module.BlacklistEmailListView
    BlacklistEmailAddView = views_module.BlacklistEmailAddView
    BlacklistEmailRemoveView = views_module.BlacklistEmailRemoveView
finally:
    # Clean up
    if _parent_dir in sys.path:
        sys.path.remove(_parent_dir)

from client_management.views_dashboard import ClientDashboardViewSet
from client_management.views.badge_views import ClientBadgeViewSet, ClientBadgeAnalyticsViewSet

router = DefaultRouter()
router.register(r'dashboard', ClientDashboardViewSet, basename='client-dashboard')
router.register(r'badges', ClientBadgeViewSet, basename='client-badges')
router.register(r'badge-analytics', ClientBadgeAnalyticsViewSet, basename='client-badge-analytics')

urlpatterns = [
    # Client Profiles
    path("clients/", views.ClientProfileListView.as_view(), name="client-list"),
    path("clients/<int:pk>/", views.ClientProfileDetailView.as_view(), name="client-detail"),
    path("clients/<int:pk>/edit/", views.ClientProfileUpdateView.as_view(), name="client-edit"),

    # Client Wallet
    path("clients/<int:client_id>/wallet/", views.ClientWalletView.as_view(), name="client-wallet"),

    # Admin Actions on Clients
    path("clients/<int:client_id>/actions/", views.ClientActionView.as_view(), name="client-actions"),

    # Profile Update Requests
    path("profile-update-requests/", views.ProfileUpdateRequestCreateView.as_view(), name="create-profile-update-request"),
    path("profile-update-requests/admin/", views.ProfileUpdateRequestListView.as_view(), name="list-profile-update-requests"),

    # Loyalty Management
    path("loyalty/tiers/", views.LoyaltyTierListView.as_view(), name="loyalty-tier-list"),
    path("loyalty/tiers/<int:pk>/", views.LoyaltyTierDetailView.as_view(), name="loyalty-tier-detail"),
    path("loyalty/transactions/<int:client_id>/", views.LoyaltyTransactionListView.as_view(), name="loyalty-transaction-list"),

    # Client Dashboard
    path("", include(router.urls)),

    path("blacklist/", BlacklistEmailListView.as_view(), name="blacklist-list"),
    path("blacklist/add/", BlacklistEmailAddView.as_view(), name="blacklist-add"),
    path("blacklist/remove/", BlacklistEmailRemoveView.as_view(), name="blacklist-remove"),
]
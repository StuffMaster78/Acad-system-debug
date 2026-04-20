"""
API URLs for the order_pricing_core app.
"""

from __future__ import annotations

from django.urls import path

from order_pricing_core.api.views.composite_quote_views import (
    CompositeQuoteCreateView,
)
from order_pricing_core.api.views.composite_quote_views import (
    CompositeQuoteDetailView,
)
from order_pricing_core.api.views.composite_quote_views import (
    CompositeQuoteFinalizeView,
)
from order_pricing_core.api.views.composite_quote_views import (
    CompositeQuoteUpdateView,
)
from order_pricing_core.api.views.design_order_quote_views import (
    DesignOrderQuoteStartView,
)
from order_pricing_core.api.views.design_order_quote_views import (
    DesignOrderQuoteUpdateView,
)
from order_pricing_core.api.views.diagram_order_quote_views import (
    DiagramOrderQuoteStartView,
)
from order_pricing_core.api.views.diagram_order_quote_views import (
    DiagramOrderQuoteUpdateView,
)
from order_pricing_core.api.views.paper_order_quote_views import (
    PaperOrderQuoteStartView,
)
from order_pricing_core.api.views.paper_order_quote_views import (
    PaperOrderQuoteUpdateView,
)
from order_pricing_core.api.views.pricing_snapshot_views import (
    PricingSnapshotCreateView,
)
from order_pricing_core.api.views.pricing_config_views import (
    AcademicLevelRateDetailView,
    WebsitePricingProfileView
)
from order_pricing_core.api.views.pricing_config_views import (
    AcademicLevelRateListCreateView,
)
from order_pricing_core.api.views.service_catalog_views import (
    ServiceAddonDetailView,
)
from order_pricing_core.api.views.service_catalog_views import (
    ServiceAddonListCreateView,
)
from order_pricing_core.api.views.service_catalog_views import (
    ServiceCatalogItemDetailView,
)
from order_pricing_core.api.views.service_catalog_views import (
    ServiceCatalogItemListCreateView,
)

urlpatterns = [
    path(
        "quotes/paper/start/",
        PaperOrderQuoteStartView.as_view(),
        name="paper-order-quote-start",
    ),
    path(
        "quotes/paper/<uuid:session_id>/update/",
        PaperOrderQuoteUpdateView.as_view(),
        name="paper-order-quote-update",
    ),
    path(
        "quotes/design/start/",
        DesignOrderQuoteStartView.as_view(),
        name="design-order-quote-start",
    ),
    path(
        "quotes/design/<uuid:session_id>/update/",
        DesignOrderQuoteUpdateView.as_view(),
        name="design-order-quote-update",
    ),
    path(
        "quotes/diagram/start/",
        DiagramOrderQuoteStartView.as_view(),
        name="diagram-order-quote-start",
    ),
    path(
        "quotes/diagram/<uuid:session_id>/update/",
        DiagramOrderQuoteUpdateView.as_view(),
        name="diagram-order-quote-update",
    ),
    path(
        "quotes/<uuid:session_id>/snapshot/",
        PricingSnapshotCreateView.as_view(),
        name="pricing-snapshot-create",
    ),
    path(
        "quotes/composite/create/",
        CompositeQuoteCreateView.as_view(),
        name="composite-quote-create",
    ),
    path(
        "quotes/composite/<uuid:session_id>/",
        CompositeQuoteDetailView.as_view(),
        name="composite-quote-detail",
    ),
    path(
        "quotes/composite/<uuid:session_id>/update/",
        CompositeQuoteUpdateView.as_view(),
        name="composite-quote-update",
    ),
    path(
        "quotes/composite/<uuid:session_id>/finalize/",
        CompositeQuoteFinalizeView.as_view(),
        name="composite-quote-finalize",
    ),
    path(
    "admin/profile/",
        WebsitePricingProfileView.as_view(),
        name="admin-pricing-profile",
    ),
    path(
        "admin/dimensions/academic-levels/",
        AcademicLevelRateListCreateView.as_view(),
        name="admin-academic-level-rate-list-create",
    ),
    path(
        "admin/dimensions/academic-levels/<int:item_id>/",
        AcademicLevelRateDetailView.as_view(),
        name="admin-academic-level-rate-detail",
    ),
    path(
        "admin/service-catalog/items/",
        ServiceCatalogItemListCreateView.as_view(),
        name="admin-service-catalog-item-list-create",
    ),
    path(
        "admin/service-catalog/items/<int:item_id>/",
        ServiceCatalogItemDetailView.as_view(),
        name="admin-service-catalog-item-detail",
    ),
    path(
        "admin/service-catalog/addons/",
        ServiceAddonListCreateView.as_view(),
        name="admin-service-addon-list-create",
    ),
    path(
        "admin/service-catalog/addons/<int:item_id>/",
        ServiceAddonDetailView.as_view(),
        name="admin-service-addon-detail",
    ),
    
]
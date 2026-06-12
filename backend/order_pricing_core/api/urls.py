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
from order_pricing_core.api.views.public_estimate_views import (
    PublicPaperEstimateView,
)
from order_pricing_core.api.views.public_config_views import (
    PublicPricingConfigView,
)
from order_pricing_core.api.views.pricing_config_views import (
    AcademicLevelRateDetailView,
    AcademicLevelRateListCreateView,
    DeadlineRateDetailView,
    DeadlineRateListCreateView,
    DiagramComplexityRateDetailView,
    DiagramComplexityRateListCreateView,
    PaperTypeRateDetailView,
    PaperTypeRateListCreateView,
    SyncOrderConfigPricingRatesView,
    SubjectCategoryDetailView,
    SubjectCategoryListCreateView,
    SubjectRateDetailView,
    SubjectRateListCreateView,
    WebsitePricingProfileView,
    WorkTypeRateDetailView,
    WorkTypeRateListCreateView,
    WriterLevelRateDetailView,
    WriterLevelRateListCreateView,
)
from order_pricing_core.api.views.service_catalog_views import (
    ServiceAddonDetailView,
    ServiceAddonListCreateView,
    ServiceCatalogItemDetailView,
    ServiceCatalogItemListCreateView,
    PublicServiceAddonListView,
)

urlpatterns = [
    path(
        "public/config/",
        PublicPricingConfigView.as_view(),
        name="public-pricing-config",
    ),
    path(
        "public/estimate/",
        PublicPaperEstimateView.as_view(),
        name="public-paper-estimate",
    ),
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
        "admin/sync-order-config-rates/",
        SyncOrderConfigPricingRatesView.as_view(),
        name="admin-sync-order-config-rates",
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
    # ── Deadline rates ─────────────────────────────────────────────────────
    path(
        "admin/dimensions/deadline-rates/",
        DeadlineRateListCreateView.as_view(),
        name="admin-deadline-rate-list-create",
    ),
    path(
        "admin/dimensions/deadline-rates/<int:item_id>/",
        DeadlineRateDetailView.as_view(),
        name="admin-deadline-rate-detail",
    ),
    # ── Paper type rates ────────────────────────────────────────────────────
    path(
        "admin/dimensions/paper-types/",
        PaperTypeRateListCreateView.as_view(),
        name="admin-paper-type-rate-list-create",
    ),
    path(
        "admin/dimensions/paper-types/<int:item_id>/",
        PaperTypeRateDetailView.as_view(),
        name="admin-paper-type-rate-detail",
    ),
    # ── Work type rates ─────────────────────────────────────────────────────
    path(
        "admin/dimensions/work-types/",
        WorkTypeRateListCreateView.as_view(),
        name="admin-work-type-rate-list-create",
    ),
    path(
        "admin/dimensions/work-types/<int:item_id>/",
        WorkTypeRateDetailView.as_view(),
        name="admin-work-type-rate-detail",
    ),
    # ── Subject rates ────────────────────────────────────────────────────────
    path(
        "admin/dimensions/subject-categories/",
        SubjectCategoryListCreateView.as_view(),
        name="admin-subject-category-list-create",
    ),
    path(
        "admin/dimensions/subject-categories/<int:item_id>/",
        SubjectCategoryDetailView.as_view(),
        name="admin-subject-category-detail",
    ),
    path(
        "admin/dimensions/subject-rates/",
        SubjectRateListCreateView.as_view(),
        name="admin-subject-rate-list-create",
    ),
    path(
        "admin/dimensions/subject-rates/<int:item_id>/",
        SubjectRateDetailView.as_view(),
        name="admin-subject-rate-detail",
    ),
    # ── Writer level rates ──────────────────────────────────────────────────
    path(
        "admin/dimensions/writer-levels/",
        WriterLevelRateListCreateView.as_view(),
        name="admin-writer-level-rate-list-create",
    ),
    path(
        "admin/dimensions/writer-levels/<int:item_id>/",
        WriterLevelRateDetailView.as_view(),
        name="admin-writer-level-rate-detail",
    ),
    # ── Diagram complexity rates ────────────────────────────────────────────
    path(
        "admin/dimensions/diagram-complexity/",
        DiagramComplexityRateListCreateView.as_view(),
        name="admin-diagram-complexity-rate-list-create",
    ),
    path(
        "admin/dimensions/diagram-complexity/<int:item_id>/",
        DiagramComplexityRateDetailView.as_view(),
        name="admin-diagram-complexity-rate-detail",
    ),
    # ── Service catalog ─────────────────────────────────────────────────────
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

    # ── Public — available addons for a service (order creation) ──────────
    path(
        "public/addons/",
        PublicServiceAddonListView.as_view(),
        name="public-service-addon-list",
    ),
]

"""
Order pricing core model exports.
"""

from order_pricing_core.models.pricing_dimensions import AcademicLevelRate
from order_pricing_core.models.pricing_dimensions import AnalysisLevelRate
from order_pricing_core.models.pricing_dimensions import DeadlineRate
from order_pricing_core.models.pricing_dimensions import DiagramComplexityRate
from order_pricing_core.models.pricing_dimensions import PaperTypeRate
from order_pricing_core.models.pricing_dimensions import SubjectCategory
from order_pricing_core.models.pricing_dimensions import SubjectRate
from order_pricing_core.models.pricing_dimensions import WorkTypeRate
from order_pricing_core.models.pricing_dimensions import WriterLevelRate
from order_pricing_core.models.pricing_profiles import WebsitePricingProfile
from order_pricing_core.models.pricing_quotes import PricingQuote
from order_pricing_core.models.pricing_quotes import PricingQuoteInput
from order_pricing_core.models.pricing_quotes import PricingQuoteLine
from order_pricing_core.models.pricing_snapshots import PricingSnapshot
from order_pricing_core.models.pricing_snapshots import PricingSnapshotLine
from order_pricing_core.models.service_catalog import DesignOrderServiceConfig
from order_pricing_core.models.service_catalog import DiagramOrderServiceConfig
from order_pricing_core.models.service_catalog import PaperOrderServiceConfig
from order_pricing_core.models.service_catalog import ServiceAddon
from order_pricing_core.models.service_catalog import ServiceAddonApplicability
from order_pricing_core.models.service_catalog import ServiceCatalogItem
from .composite_quotes import CompositePricingQuote
from .composite_quotes import CompositePricingQuoteItem
from .calculator_session import PricingCalculatorSession

# Compat stubs — these models were in the old monolithic models.py which is
# now shadowed by this package. They have no DB tables (never migrated).
class _LegacyStub:
    """No-op stub for unmigrated legacy models."""
    objects = type("Manager", (), {"filter": lambda *a, **k: [], "get": lambda *a, **k: None, "create": lambda *a, **k: None})()

class PricingConfiguration(_LegacyStub):
    pass

class AcademicLevelPricing(_LegacyStub):
    pass

class WriterLevelOptionConfig(_LegacyStub):
    pass

class AdditionalService(_LegacyStub):
    pass

class PreferredWriterConfig(_LegacyStub):
    pass
__all__ = [
    "AcademicLevelRate",
    "AnalysisLevelRate",
    "DeadlineRate",
    "DiagramComplexityRate",
    "PaperTypeRate",
    "SubjectCategory",
    "SubjectRate",
    "WorkTypeRate",
    "WriterLevelRate",
    "WebsitePricingProfile",
    "PricingQuote",
    "PricingQuoteInput",
    "PricingQuoteLine",
    "PricingSnapshot",
    "PricingSnapshotLine",
    "DesignOrderServiceConfig",
    "DiagramOrderServiceConfig",
    "PaperOrderServiceConfig",
    "ServiceAddon",
    "ServiceAddonApplicability",
    "ServiceCatalogItem",
    "CompositePricingQuote",
    "CompositePricingQuoteItem",
]
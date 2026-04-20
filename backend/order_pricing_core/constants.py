"""
Constants for the orders_pricing_core app.

This module defines stable, code-controlled choices used by the
pricing engine, serializers, calculators, and internal workflows.

These constants represent system structure, not business-configurable
data. Admin-managed business options such as academic levels, paper
types, subjects, and addons must live in database models instead.
"""

from __future__ import annotations


class ServiceFamily:
    """
    Top-level pricing families supported by normal order flow.
    """

    PAPER_ORDER = "paper_order"
    DESIGN_ORDER = "design_order"
    DIAGRAM_ORDER = "diagram_order"

    CHOICES = (
        (PAPER_ORDER, "Paper Order"),
        (DESIGN_ORDER, "Design Order"),
        (DIAGRAM_ORDER, "Diagram Order"),
    )


class PricingStrategy:
    """
    Supported pricing strategies for orderable services.
    """

    FORMULA = "formula"
    FIXED = "fixed"
    HYBRID = "hybrid"

    CHOICES = (
        (FORMULA, "Formula"),
        (FIXED, "Fixed"),
        (HYBRID, "Hybrid"),
    )


class PricingUnit:
    """
    Supported units used by the pricing engine.

    PAGE
        Used for paper-based orders.

    SLIDE
        Used for presentations.

    ITEM
        Used for fixed design products such as posters, brochures,
        flyers, and similar one-off deliverables.

    QUANTITY
        Used where multiple identical items are sold in one order.

    ORDER
        Used for flat-priced order-level services.

    DIAGRAM
        Used for ERDs, flowcharts, UML diagrams, and similar
        diagram-based deliverables.
    """

    PAGE = "page"
    SLIDE = "slide"
    ITEM = "item"
    QUANTITY = "quantity"
    ORDER = "order"
    DIAGRAM = "diagram"

    CHOICES = (
        (PAGE, "Page"),
        (SLIDE, "Slide"),
        (ITEM, "Item"),
        (QUANTITY, "Quantity"),
        (ORDER, "Order"),
        (DIAGRAM, "Diagram"),
    )


class QuoteStatus:
    """
    Lifecycle statuses for pricing quotes.
    """

    DRAFT = "draft"
    ESTIMATED = "estimated"
    CALCULATED = "calculated"
    FINALIZED = "finalized"
    CONVERTED = "converted"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

    CHOICES = (
        (DRAFT, "Draft"),
        (ESTIMATED, "Estimated"),
        (CALCULATED, "Calculated"),
        (FINALIZED, "Finalized"),
        (CONVERTED, "Converted"),
        (EXPIRED, "Expired"),
        (CANCELLED, "Cancelled"),
    )


class QuoteMode:
    """
    Modes used while pricing a quote.

    ESTIMATE
        Used for early-step quoting where the client may only have
        supplied partial inputs.

    FINAL
        Used once enough inputs are present to compute the actual
        payable amount.
    """

    ESTIMATE = "estimate"
    FINAL = "final"

    CHOICES = (
        (ESTIMATE, "Estimate"),
        (FINAL, "Final"),
    )


class BreakdownLineType:
    """
    Internal quote and snapshot breakdown line types.
    """

    BASE = "base"
    MULTIPLIER = "multiplier"
    FIXED_FEE = "fixed_fee"
    ADDON = "addon"
    DISCOUNT = "discount"
    TOTAL = "total"

    CHOICES = (
        (BASE, "Base"),
        (MULTIPLIER, "Multiplier"),
        (FIXED_FEE, "Fixed Fee"),
        (ADDON, "Addon"),
        (DISCOUNT, "Discount"),
        (TOTAL, "Total"),
    )


class SpacingMode:
    """
    Supported spacing modes for paper-based orders.

    Double spacing is the default business basis.
    Single spacing is charged at a multiplier configured in the
    pricing profile, which is expected to default to 2.0.
    """

    DOUBLE = "double"
    SINGLE = "single"

    CHOICES = (
        (DOUBLE, "Double"),
        (SINGLE, "Single"),
    )

    DEFAULT = DOUBLE


class WriterSelectionMode:
    """
    Writer-related selection modes used in pricing flows.

    STANDARD
        Default writer selection with no extra fee.

    WRITER_LEVEL
        Tier-based upsell such as standard, advanced, or premium.
        This is not tied to a specific writer.

    PREFERRED_WRITER
        Specific writer selected by the client. This should draw
        a preferred writer fee.
    """

    STANDARD = "standard"
    WRITER_LEVEL = "writer_level"
    PREFERRED_WRITER = "preferred_writer"

    CHOICES = (
        (STANDARD, "Standard"),
        (WRITER_LEVEL, "Writer Level"),
        (PREFERRED_WRITER, "Preferred Writer"),
    )


class DesignProductType:
    """
    Standardized design products supported in normal order flow.
    """

    PRESENTATION = "presentation"
    BROCHURE = "brochure"
    CATALOGUE = "catalogue"
    POSTER = "poster"
    FLYER = "flyer"
    INFOGRAPHIC = "infographic"

    CHOICES = (
        (PRESENTATION, "Presentation"),
        (BROCHURE, "Brochure"),
        (CATALOGUE, "Catalogue"),
        (POSTER, "Poster"),
        (FLYER, "Flyer"),
        (INFOGRAPHIC, "Infographic"),
    )


class DesignPackageType:
    """
    Package tiers for standardized design products.

    These are intentionally limited and code-controlled. Admins may
    price them differently per website, but they should not invent
    arbitrary package mechanics in the dashboard.
    """

    STANDARD = "standard"
    PREMIUM = "premium"
    CUSTOM = "custom"

    CHOICES = (
        (STANDARD, "Standard"),
        (PREMIUM, "Premium"),
        (CUSTOM, "Custom"),
    )


class DiagramType:
    """
    Standard diagram deliverables supported by normal order flow.
    """

    FLOWCHART = "flowchart"
    ERD = "erd"
    UML = "uml"
    PROCESS_DIAGRAM = "process_diagram"
    SYSTEM_DIAGRAM = "system_diagram"

    CHOICES = (
        (FLOWCHART, "Flowchart"),
        (ERD, "ERD"),
        (UML, "UML Diagram"),
        (PROCESS_DIAGRAM, "Process Diagram"),
        (SYSTEM_DIAGRAM, "System Diagram"),
    )


class DiagramComplexity:
    """
    Complexity levels for diagram-based work.

    These levels are meant to support predictable pricing for
    diagrams without over-modeling diagram internals too early.
    """

    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"

    CHOICES = (
        (SIMPLE, "Simple"),
        (MODERATE, "Moderate"),
        (COMPLEX, "Complex"),
    )


class AnalysisLevel:
    """
    Analysis intensity levels for paper-based work.

    This is used for work involving calculations, data handling,
    advanced charts, Excel workbooks, SPSS outputs, or similar
    analysis-heavy effort.

    Charts themselves are not modeled as standalone pricing units.
    Basic charts are assumed to be included where appropriate.
    Advanced analysis and deliverables should be priced via this
    level and/or applicable addons.
    """

    NONE = "none"
    BASIC = "basic"
    ADVANCED = "advanced"

    CHOICES = (
        (NONE, "None"),
        (BASIC, "Basic"),
        (ADVANCED, "Advanced"),
    )


class DeadlinePolicy:
    """
    Deadline policy constants for page-based urgent order handling.

    These values support the agreed business rule that double-spaced
    work is the default basis and that urgent order suggestions should
    be driven by pages-to-hours expectations.

    DEFAULT_PAGES_PER_HOUR
        Normal baseline used for recommendation logic.

    EXTRA_HOUR_PER_EXTRA_PAGE
        Used when suggesting safer deadlines for larger page counts.

    HARD_REJECT_ENABLED
        The core can either hard reject impossible combinations or
        return soft recommendations with rush pricing. The current
        business direction is to prefer recommendation-first behavior.
    """

    DEFAULT_PAGES_PER_HOUR = 1
    EXTRA_HOUR_PER_EXTRA_PAGE = 1
    HARD_REJECT_ENABLED = False


class SuggestionType:
    """
    Suggestion types returned by validation or quote guidance logic.
    """

    DEADLINE_ADJUSTMENT = "deadline_adjustment"
    PAGE_ADJUSTMENT = "page_adjustment"
    RUSH_ORDER = "rush_order"

    CHOICES = (
        (DEADLINE_ADJUSTMENT, "Deadline Adjustment"),
        (PAGE_ADJUSTMENT, "Page Adjustment"),
        (RUSH_ORDER, "Rush Order"),
    )
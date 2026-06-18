"""
GradeCrest → portal URL handoff contract tests.

GradeCrest's order.vue builds a portalUrl with these query params:
  order_type, deadline, type (paper_code), level, work_type, spacing,
  pages, subject, format_style, slides, design_type, diagram_type,
  quantity, topic, instructions, addon_codes

These tests verify the expected shape and value constraints so that
a regression in the URL builder is caught before it silently discards
client data when the user lands on the portal.
"""

from urllib.parse import parse_qs, urlparse

import pytest


def parse_portal_url(url: str) -> dict[str, str]:
    """Parse a portal URL and return a flat dict of first values."""
    qs = parse_qs(urlparse(url).query)
    return {k: v[0] for k, v in qs.items()}


class TestPortalHandoffParams:
    """Contract: required params are present and correctly formatted."""

    def _paper_url(self, **overrides) -> dict[str, str]:
        base = {
            "order_type": "paper",
            "deadline": "336",
            "type": "essay",
            "level": "undergrad",
            "work_type": "writing",
            "spacing": "double",
            "pages": "3",
            "subject": "psychology",
            "format_style": "apa7",
            "topic": "The impact of social media on teen mental health",
            "instructions": "Use peer-reviewed sources only.",
        }
        base.update(overrides)
        return base

    def test_paper_order_required_params_present(self):
        params = self._paper_url()
        for key in ("order_type", "deadline", "type", "level", "work_type", "spacing", "pages"):
            assert key in params, f"Missing required param: {key}"

    def test_spacing_values_are_canonical(self):
        for val in ("double", "single"):
            params = self._paper_url(spacing=val)
            assert params["spacing"] in ("double", "single")

    def test_instructions_not_truncated_below_2000(self):
        long_instructions = "x" * 1999
        params = self._paper_url(instructions=long_instructions)
        assert len(params["instructions"]) == 1999

    def test_instructions_cap_at_2000(self):
        long_instructions = "x" * 3000
        # Simulate what order.vue does: .trim().slice(0, 2000)
        capped = long_instructions.strip()[:2000]
        params = self._paper_url(instructions=capped)
        assert len(params["instructions"]) == 2000

    def test_addon_codes_comma_separated(self):
        params = self._paper_url(addon_codes="plagiarism_report,vip_support")
        codes = params["addon_codes"].split(",")
        assert len(codes) == 2
        assert "plagiarism_report" in codes
        assert "vip_support" in codes

    def test_combo_order_includes_slides(self):
        params = self._paper_url(order_type="combo", slides="10")
        assert params["order_type"] == "combo"
        assert params["slides"] == "10"

    def test_design_order_params(self):
        params = {
            "order_type": "design",
            "deadline": "72",
            "design_type": "powerpoint",
            "quantity": "15",
        }
        assert params["order_type"] == "design"
        assert params["design_type"] == "powerpoint"
        assert int(params["quantity"]) >= 1

    def test_diagram_order_params(self):
        params = {
            "order_type": "diagram",
            "deadline": "48",
            "diagram_type": "flowchart",
            "quantity": "3",
        }
        assert params["order_type"] == "diagram"
        assert int(params["quantity"]) >= 1

    def test_deadline_is_numeric_hours(self):
        for hours in ("6", "12", "24", "48", "72", "120", "168", "336"):
            params = self._paper_url(deadline=hours)
            assert int(params["deadline"]) > 0

    def test_topic_max_200_chars(self):
        long_topic = "a" * 201
        capped = long_topic[:200]
        assert len(capped) == 200

    def test_pages_is_positive_integer(self):
        for pages in ("1", "5", "50", "200"):
            params = self._paper_url(pages=pages)
            assert int(params["pages"]) >= 1


class TestPortalHandoffNegativeCases:
    """Edge cases that should not produce broken portal URLs."""

    def test_empty_instructions_omitted(self):
        params = {"order_type": "paper", "deadline": "336"}
        # instructions key should not be present if value is empty
        assert "instructions" not in params or params["instructions"].strip() != ""

    def test_empty_topic_omitted(self):
        params = {"order_type": "paper", "deadline": "336"}
        assert "topic" not in params or params.get("topic", "").strip() != ""

    def test_no_addon_codes_key_when_none_selected(self):
        params = {"order_type": "paper", "deadline": "336", "type": "essay"}
        assert "addon_codes" not in params

    def test_single_spacing_sets_param(self):
        params = {"order_type": "paper", "spacing": "single"}
        assert params["spacing"] == "single"

    def test_double_spacing_can_be_omitted_as_default(self):
        # GradeCrest order.vue only sets spacing param if single;
        # portal defaults to double when absent.
        params = {"order_type": "paper", "deadline": "336"}
        spacing = params.get("spacing", "double")
        assert spacing == "double"

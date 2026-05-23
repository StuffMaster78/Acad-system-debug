"""
Tests for cms_core validators.
"""

import pytest
from cms_core.validators import (
    ValidationResult,
    _count_words_in_streamfield,
    generate_toc,
    get_reading_time,
    validate_page_for_publish,
)


class TestValidationResult:
    def test_empty_result_is_publishable(self):
        result = ValidationResult()
        assert result.is_publishable is True
        assert result.blockers == []
        assert result.warnings == []
        assert result.suggestions == []

    def test_blocker_prevents_publish(self):
        result = ValidationResult()
        result.add_blocker("Missing title")
        assert result.is_publishable is False

    def test_warning_allows_publish(self):
        result = ValidationResult()
        result.add_warning("Short content")
        assert result.is_publishable is True

    def test_to_dict(self):
        result = ValidationResult()
        result.add_blocker("Error", field="title")
        result.add_warning("Note")
        result.add_suggestion("Idea")
        data = result.to_dict()
        assert data["is_publishable"] is False
        assert len(data["blockers"]) == 1
        assert len(data["warnings"]) == 1
        assert len(data["suggestions"]) == 1


class TestReadingTime:
    def test_under_one_minute(self):
        assert get_reading_time(100) == "Under 1 min read"

    def test_one_minute(self):
        assert get_reading_time(300) == "1 min read"

    def test_five_minutes(self):
        assert get_reading_time(1250) == "5 min read"


class TestTOCGeneration:
    def test_empty_body(self):
        assert generate_toc([]) == []

    def test_generates_anchors(self):

        class FakeBlock:
            def __init__(self, block_type, value):
                self.block_type = block_type
                self.value = value

        blocks = [
            FakeBlock("heading", {"text": "Introduction", "level": "h2"}),
            FakeBlock("paragraph", "<p>Some text</p>"),
            FakeBlock("heading", {"text": "Step One", "level": "h3"}),
        ]
        toc = generate_toc(blocks)
        assert len(toc) == 2
        assert toc[0]["level"] == "h2"
        assert toc[0]["text"] == "Introduction"
        assert toc[0]["anchor_id"] == "introduction"
        assert toc[1]["level"] == "h3"

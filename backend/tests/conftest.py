from __future__ import annotations

pytest_plugins = [
    "tests.fixtures.database_fixtures",
    "tests.fixtures.website_fixtures",
    "tests.fixtures.auth_fixtures",
    "tests.fixtures.client_fixtures",
    "tests.fixtures.order_fixtures",
    "tests.fixtures.payment_fixtures",
    "tests.fixtures.writer_fixtures",
    "tests.fixtures.wagtail_fixtures",
    "tests.fixtures.cms_fixtures",
    "tests.fixtures.mock_fixtures",
]
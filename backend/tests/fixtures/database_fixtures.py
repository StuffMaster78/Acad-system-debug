from __future__ import annotations

import pytest


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    """
    Set up the test database once per session.
    """

    from django.apps import apps
    from django.contrib.contenttypes.management import create_contenttypes
    from django.core.management import call_command
    from django.db import connection

    with django_db_blocker.unblock():
        try:
            call_command(
                "migrate",
                verbosity=0,
                interactive=False,
                run_syncdb=False,
            )
        except Exception as exc:
            print(f"Migration warning: {exc}")

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM django_content_type
                    WHERE name IS NULL
                    OR name = ''
                    OR (app_label = 'migrations' AND model = 'migration')
                    """
                )
        except Exception as exc:
            message = str(exc).lower()
            if "does not exist" not in message and "relation" not in message:
                print(f"Content type cleanup: {exc}")

        try:
            for app_config in apps.get_app_configs():
                if app_config.label == "migrations":
                    continue

                if not app_config.models_module:
                    continue

                try:
                    create_contenttypes(
                        app_config,
                        verbosity=0,
                        interactive=False,
                    )
                except Exception:
                    pass
        except Exception as exc:
            print(f"Content types setup: {exc}")


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """
    Enable database access for all tests.
    """
    pass
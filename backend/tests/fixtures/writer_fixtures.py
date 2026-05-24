from __future__ import annotations

import pytest


@pytest.fixture
def writer_profile(writer_user, website):
    from writer_management.models import WriterProfile

    profile, _ = WriterProfile.objects.get_or_create(
        user=writer_user,
        website=website,
        defaults={
            "is_available_for_auto_assignments": True,
            "verification_status": "verified",
        },
    )
    return profile
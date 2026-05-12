from activity.services.metadata_sanitizer import (
    ActivityMetadataSanitizer,
)


def test_sanitizer_removes_sensitive_keys():
    metadata = {
        "safe": "yes",
        "password": "123",
        "token": "abc",
        "nested": {
            "otp": "0000",
            "ok": True,
        },
    }

    result = ActivityMetadataSanitizer.sanitize(metadata)

    assert "password" not in result
    assert "token" not in result
    assert "otp" not in result["nested"]
    assert result["safe"] == "yes"
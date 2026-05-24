from __future__ import annotations

import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_request_session():
    session = MagicMock()
    session.session_key = "test-session-key-12345"
    session._session = {}

    def session_get(key, default=None):
        return session._session.get(key, default)

    def session_set(key, value):
        session._session[key] = value

    def session_pop(key, default=None):
        return session._session.pop(key, default)

    session.get = session_get
    session.__getitem__ = lambda self, key: session._session[key]
    session.__setitem__ = lambda self, key, value: session_set(key, value)
    session.__contains__ = lambda self, key: key in session._session
    session.pop = session_pop
    session.flush = MagicMock()
    session.save = MagicMock()
    session.set_expiry = MagicMock()
    session.modified = False

    return session


@pytest.fixture
def mock_request(mock_request_session):
    request = MagicMock()
    request.data = {}
    request.headers = {"User-Agent": "Test Agent"}
    request.session = mock_request_session
    request.get_host = MagicMock(return_value="test.local")
    request.META = {"REMOTE_ADDR": "127.0.0.1"}

    return request
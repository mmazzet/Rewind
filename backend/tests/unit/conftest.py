from unittest.mock import AsyncMock

import pytest


@pytest.fixture
def mock_db():
    return AsyncMock()

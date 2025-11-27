"""Pytest configuration."""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock


@pytest.fixture
def test_images_dir():
    """Fixture for test images directory."""
    return Path("tests/test_images")


@pytest.fixture
def temp_log_file():
    """Fixture for temporary log file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
        temp_path = f.name
    
    yield temp_path
    
    # 清理
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def mock_mcp_callback():
    """Fixture for mock MCP callback function."""
    return Mock()







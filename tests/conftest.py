"""Pytest configuration for VideoCraft.

Automatically enables lightweight test mode to avoid loading heavy ML
frameworks (torch/transformers) for fast unit tests focused on core
logic and fallbacks. Override by running with LIGHT_TEST_MODE=0.
"""
import os
import pytest
import pytest

def pytest_configure():  # pragma: no cover
    os.environ.setdefault('LIGHT_TEST_MODE', '1')
    # Register custom markers to avoid warnings on CI output
    for marker in [
        'heavy: marks tests that load large ML models (deselected in fast CI)',
        'integration: multi-component integration tests',
        'slow: longer-running tests',
    ]:
        try:  # pytest <8 compatibility
            pytest.config.addinivalue_line('markers', marker)  # type: ignore[attr-defined]
        except Exception:  # pragma: no cover
            pass


def pytest_runtest_setup(item):  # pragma: no cover
    if os.getenv('LIGHT_TEST_MODE') == '1' and 'heavy' in item.keywords:
        pytest.skip('Skipping heavy test in LIGHT_TEST_MODE=1')
    # Register custom markers to avoid warnings
    for marker in [
        'heavy: marks tests that load large ML models (deselected in fast CI)',
        'integration: multi-component integration tests',
        'slow: longer-running tests',
    ]:
        try:
            pytest.config.addinivalue_line('markers', marker)  # type: ignore[attr-defined]
        except Exception:
            pass


def pytest_runtest_setup(item):  # pragma: no cover
    # Skip heavy tests automatically in lightweight mode
    if os.getenv('LIGHT_TEST_MODE') == '1' and 'heavy' in item.keywords:
        pytest.skip('Skipping heavy test in LIGHT_TEST_MODE=1')

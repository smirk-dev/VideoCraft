"""Pytest configuration for VideoCraft.

Automatically enables lightweight test mode to avoid loading heavy ML
frameworks (torch/transformers) for fast unit tests focused on core
logic and fallbacks. Override by running with LIGHT_TEST_MODE=0.
"""
import os

def pytest_configure():  # pragma: no cover
    os.environ.setdefault('LIGHT_TEST_MODE', '1')

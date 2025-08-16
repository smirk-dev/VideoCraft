import pytest

from src.ai_models import ModelRegistry


def test_registry_light_mode(monkeypatch):
    monkeypatch.setenv('LIGHT_TEST_MODE', '1')
    pipe = ModelRegistry.get_pipeline('text-classification', 'distilbert-base-uncased')
    assert pipe is None


@pytest.mark.heavy
def test_registry_attempt_load(monkeypatch):
    monkeypatch.setenv('LIGHT_TEST_MODE', '0')
    pipe = ModelRegistry.get_pipeline('text-classification', 'distilbert-base-uncased')
    assert pipe is None or hasattr(pipe, '__call__')

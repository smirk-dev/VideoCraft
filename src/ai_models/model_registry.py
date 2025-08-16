"""Central registry for heavy AI model instances.

Provides lazy, singleton-style access so multiple components can share
loaded transformer pipelines without duplicating memory usage.

Design goals:
 - Lazy: nothing heavy loads until first requested.
 - Resilient: failures are logged and a None or lightweight stub is returned.
 - Aware of LIGHT_TEST_MODE: skips heavy loads when lightweight mode active.
"""
from __future__ import annotations

import os
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ModelRegistry:
    _instances: Dict[str, Any] = {}
    _failures: Dict[str, str] = {}
    _attempted: set[str] = set()

    @classmethod
    def is_light_mode(cls) -> bool:
        return os.getenv("LIGHT_TEST_MODE") == "1"

    @classmethod
    def get_pipeline(cls, task: str, model_name: str, key: Optional[str] = None, **pipeline_kwargs) -> Any:
        """Get (or load) a transformers pipeline.

        Args:
            task: Pipeline task (e.g., 'text-classification')
            model_name: Hugging Face model id
            key: Optional unique key; if omitted derived from task+model
            **pipeline_kwargs: Extra args forwarded to pipeline()
        Returns:
            pipeline object or None if unavailable
        """
        cache_key = key or f"{task}:{model_name}"
        if cache_key in cls._instances:
            return cls._instances[cache_key]
        if cls.is_light_mode():
            logger.debug("LIGHT_TEST_MODE active; skipping load for %s", cache_key)
            return None
        if cache_key in cls._failures:
            return None
        if cache_key in cls._attempted:
            return None
        cls._attempted.add(cache_key)
        try:
            from transformers import pipeline  # local import for performance when unused
            pipe = pipeline(task, model=model_name, **pipeline_kwargs)
            cls._instances[cache_key] = pipe
            logger.info("Loaded pipeline %s", cache_key)
            return pipe
        except Exception as e:  # noqa: BLE001
            msg = f"Failed loading pipeline {cache_key}: {e}".strip()
            cls._failures[cache_key] = msg
            logger.warning(msg)
            return None

    @classmethod
    def status(cls) -> Dict[str, Dict[str, str]]:
        return {
            "loaded": {k: type(v).__name__ for k, v in cls._instances.items()},
            "failures": cls._failures.copy(),
        }


__all__ = ["ModelRegistry"]

"""Quick verification script for full (non-lightweight) model availability.

Run after installing full requirements to see which heavy AI models loaded.

Usage (PowerShell):
  $env:LIGHT_TEST_MODE='0'
  python scripts/verify_full_models.py
"""
from __future__ import annotations

import os
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("verify")


def main() -> int:
    if os.getenv("LIGHT_TEST_MODE") == "1":
        logger.warning("LIGHT_TEST_MODE=1 detected; unset to test full models.")
    try:
        from src.ai_models import (
            EmotionDetector,
            AdvancedEmotionDetector,
            IntelligentContentAnalyzer,
            ModelRegistry,
        )
    except Exception as e:  # noqa: BLE001
        logger.error("Failed to import ai_models package: %s", e)
        return 1

    import yaml
    config_path = Path("config.yaml")
    if config_path.exists():
        config = yaml.safe_load(config_path.read_text()) or {}
    else:
        config = {"models": {}}

    logger.info("Instantiating EmotionDetector…")
    emo = EmotionDetector(config)
    logger.info("Instantiating AdvancedEmotionDetector…")
    adv = AdvancedEmotionDetector(config)
    logger.info("Instantiating IntelligentContentAnalyzer…")
    ica = IntelligentContentAnalyzer(config)

    status = {
        "registry": ModelRegistry.status(),
        "emotion_detector": {
            "text_model": bool(getattr(emo, "text_emotion", None)),
            "speech_model": bool(getattr(emo, "speech_emotion", None)),
        },
        "advanced_emotion_detector": {
            "text": bool(getattr(adv, "text_emotion", None)),
            "speech": bool(getattr(adv, "speech_emotion", None)),
            "facial": bool(getattr(adv, "facial_emotion", None)),
        },
        "intelligent_content_analyzer": {
            "classifier": bool(getattr(ica, "content_classifier", None)),
            "object_detector": bool(getattr(ica, "object_detector", None)),
            "text_analyzer": bool(getattr(ica, "text_analyzer", None)),
        },
    }

    print(json.dumps(status, indent=2))
    if status["registry"]["failures"]:
        logger.warning("Some models failed to load; see 'failures' section above.")
    else:
        logger.info("All requested pipelines loaded (or were not needed).")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

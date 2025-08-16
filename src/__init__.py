"""VideoCraft core package.

Lightweight __init__ to avoid importing heavy ML/video dependencies (torch, transformers, cv2, etc.)
during simple operations or unit tests that only need small utility/data classes.

Public symbols are exposed lazily through __getattr__ to keep import cost minimal.
"""

from importlib import import_module
from typing import Any

__version__ = "1.0.0"
__author__ = "AI Film Editor Team"
__email__ = "contact@aifilmeditor.com"

# Mapping of attribute name -> (module_path, symbol_name)
_LAZY_MAP = {
    # Processors
    'VideoAnalyzer': ('src.processors.video_analyzer', 'VideoAnalyzer'),
    'ScriptParser': ('src.processors.script_parser', 'ScriptParser'),
    'AudioAnalyzer': ('src.processors.audio_analyzer', 'AudioAnalyzer'),
    'SceneDetector': ('src.processors.scene_detector', 'SceneDetector'),
    # AI Models
    'EmotionDetector': ('src.ai_models.emotion_detector', 'EmotionDetector'),
    'SentimentAnalyzer': ('src.ai_models.sentiment_analyzer', 'SentimentAnalyzer'),
    'VisualAnalyzer': ('src.ai_models.visual_analyzer', 'VisualAnalyzer'),
    # Suggestions
    'CutSuggester': ('src.suggestions.cut_suggester', 'CutSuggester'),
    'TransitionRecommender': ('src.suggestions.transition_recommender', 'TransitionRecommender'),
    # UI
    'TimelineViewer': ('src.ui.timeline_viewer', 'TimelineViewer'),
    'SuggestionPanel': ('src.ui.suggestion_panel', 'SuggestionPanel'),
    # Utils
    'FileHandler': ('src.utils.file_handler', 'FileHandler'),
    'TimelineSync': ('src.utils.timeline_sync', 'TimelineSync'),
}

__all__ = list(_LAZY_MAP.keys()) + ['__version__', '__author__', '__email__']


def __getattr__(name: str) -> Any:  # pragma: no cover - simple passthrough
    """Dynamically import symbols on first access.

    This prevents unnecessary heavy imports (e.g., torch) when only lightweight
    components (like dataclasses) are needed in tests.
    """
    if name in _LAZY_MAP:
        module_path, symbol = _LAZY_MAP[name]
        try:
            module = import_module(module_path)
            obj = getattr(module, symbol)
            globals()[name] = obj  # cache for future lookups
            return obj
        except Exception as e:  # Keep failure silent but explicit
            raise ImportError(f"Failed to lazily import '{name}' from '{module_path}': {e}") from e
    raise AttributeError(f"module 'src' has no attribute '{name}'")

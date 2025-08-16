"""Suggestion engines (lazy exports).

We defer importing heavy modules until symbols are actually used to keep
test startup lightweight when only dataclasses/utilities are needed.
"""

from importlib import import_module
from typing import Any

_LAZY = {
	'CutSuggester': ('src.suggestions.cut_suggester', 'CutSuggester'),
	'TransitionRecommender': ('src.suggestions.transition_recommender', 'TransitionRecommender'),
}

__all__ = list(_LAZY.keys())

def __getattr__(name: str) -> Any:  # pragma: no cover
	if name in _LAZY:
		mod_path, sym = _LAZY[name]
		module = import_module(mod_path)
		obj = getattr(module, sym)
		globals()[name] = obj
		return obj
	raise AttributeError(f"module 'src.suggestions' has no attribute '{name}'")

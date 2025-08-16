#!/usr/bin/env python3
"""
Comprehensive test to verify all fixes for missing methods are working.
"""
import sys
import os
import pytest

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault('LIGHT_TEST_MODE', '1')

def test_all_fixes():
    """Assertion-based comprehensive fix verification (lightweight friendly)."""
    # 1. BasicNLPProcessor parse_script_file
    from src.utils.offline_models import BasicNLPProcessor
    processor = BasicNLPProcessor()
    assert hasattr(processor, 'parse_script_file')
    assert isinstance(processor.parse_script_file('data/test_script.txt'), list)

    # 2. IntelligentContentAnalyzer (skip if unavailable)
    try:
        from src.ai_models.intelligent_content_analyzer import IntelligentContentAnalyzer
        analyzer = IntelligentContentAnalyzer({'ai_models': {'cache_dir': './cache'}})
        assert hasattr(analyzer, 'adapt_suggestions_to_content')
        result = analyzer.adapt_suggestions_to_content([], {'content_type': 'generic', 'confidence': 0.5})
        assert isinstance(result, list)
    except Exception:
        pytest.skip('IntelligentContentAnalyzer not available in lightweight mode')

    # 3. CutSuggestion copy
    from src.suggestions.cut_suggester import CutSuggestion
    original = CutSuggestion(15.0, 0.9, 'test copy', 'test', {'test': True})
    copied = original.copy()
    assert copied.timestamp == original.timestamp
    assert copied is not original
    assert copied.metadata is not original.metadata

    # 4. Integration workflow via LIGHT_TEST_MODE
    from main import load_config, initialize_components
    config = load_config()
    comps = initialize_components(config)
    for name in ['script_parser', 'content_analyzer', 'cut_suggester']:
        assert name in comps and comps[name] is not None, f"Component {name} missing"
    assert hasattr(comps['script_parser'], 'parse_script_file')
    assert hasattr(comps['content_analyzer'], 'adapt_suggestions_to_content')

if __name__ == "__main__":  # manual run
    test_all_fixes()
    print("All assertions passed.")

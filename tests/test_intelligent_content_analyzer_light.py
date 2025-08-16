from src.ai_models.intelligent_content_analyzer import IntelligentContentAnalyzer


def test_content_analyzer_light_mode(monkeypatch):
    monkeypatch.setenv('LIGHT_TEST_MODE', '1')
    analyzer = IntelligentContentAnalyzer({'ai_models': {'cache_dir': './cache'}})
    assert analyzer.content_classifier is None
    assert analyzer.object_detector is None
    assert analyzer.text_analyzer is None


def test_content_analyzer_basic_analysis(monkeypatch, tmp_path):
    monkeypatch.setenv('LIGHT_TEST_MODE', '1')
    analyzer = IntelligentContentAnalyzer({'ai_models': {'cache_dir': './cache'}})
    dummy_video = tmp_path / 'dummy.mp4'
    dummy_video.write_bytes(b'')
    result = analyzer.analyze_content(str(dummy_video))
    assert 'content_type' in result
    assert 'editing_recommendations' in result

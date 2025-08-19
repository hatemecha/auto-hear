import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from auto_hear import MusicAnalyzerGUI


class DummyText:
    def __init__(self):
        self.content = ""

    def config(self, **kwargs):
        pass

    def delete(self, *args, **kwargs):
        self.content = ""

    def insert(self, *args):
        text = args[-1] if args else ""
        self.content += text

    def get(self, *args, **kwargs):
        return self.content


class DummyVar:
    def __init__(self, value):
        self._value = value

    def get(self):
        return self._value


def _make_app():
    app = MusicAnalyzerGUI.__new__(MusicAnalyzerGUI)
    app.details_text = DummyText()
    app.silence_threshold_var = DummyVar(-40)
    app.min_silence_var = DummyVar(0.5)
    app.analysis_results = {
        "file_path": "dummy.wav",
        "duration": 1.23,
        "audio_info": {"sample_rate": 44100, "samples": 12345},
        "bpm_analysis": {
            "bpm": 120.0,
            "confidence": 0.9,
            "method": "test",
            "tempo_stability": 0.3,
            "beats_detected": 10,
            "beats": [],
            "all_estimates": [
                {"bpm": 120.0, "confidence": 0.9, "method": "test"}
            ],
        },
        "key_analysis": {
            "key": "C",
            "scale": "major",
            "confidence": 0.8,
            "method": "test",
            "key_stability": 0.9,
            "key_changes_detected": False,
        },
        "silence_analysis": {
            "segments_found": 0,
            "segments": [],
            "total_silence_duration": 0.0,
        },
    }
    return app


def test_update_details_display_renders_without_error():
    app = _make_app()
    app.update_details_display()
    content = app.details_text.get()
    assert "=== ANÁLISIS BPM ===" in content

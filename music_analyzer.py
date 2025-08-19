"""Music analysis utilities for auto_hear GUI.

This module provides a :class:`MusicAnalyzer` capable of extracting
basic musical features from an audio file and a convenience function
:func:`analyze_audio_file` to use it directly.  The analyser attempts to
use :mod:`librosa` for the heavy lifting but degrades gracefully if the
library or the audio file is unavailable.

The returned dictionary mirrors the structure expected by
``auto_hear.py``.  Keys include ``bpm_analysis``, ``key_analysis`` and
``silence_analysis`` alongside information about the audio file itself.
If an error occurs, a dictionary containing the keys ``error`` and
``file_path`` is returned instead.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Dict, Any, List, Tuple

# Optional imports – we try to import lazily inside methods to allow the
# module to be imported even when the heavy dependencies are missing.


@dataclass
class MusicAnalyzer:
    """High level audio analyser used by :mod:`auto_hear`.

    The class focuses on three pieces of information: tempo (BPM),
    musical key and silence detection.  The implementation favours
    robustness over cutting edge accuracy; if the analysis fails the
    error is propagated in a controlled manner.

    Parameters
    ----------
    silence_threshold:
        Threshold in decibels below which a portion of the audio is
        considered silent.  Typical values are around ``-40``.
    min_silence_duration:
        Minimum duration in seconds for a silence segment to be
        reported.
    """

    silence_threshold: float = -40.0
    min_silence_duration: float = 0.5

    # ------------------------------------------------------------------
    def analyze_song(self, file_path: str, *, verbose: bool = False) -> Dict[str, Any]:
        """Analyse ``file_path`` and return a dictionary with results.

        The dictionary structure is purposely designed to satisfy the
        expectations of ``auto_hear.py``.  In case of an error the return
        value is ``{"error": <message>, "file_path": file_path}``.

        Parameters
        ----------
        file_path:
            Path to the audio file to analyse.
        verbose:
            Currently unused but kept for API compatibility.
        """

        if not os.path.isfile(file_path):
            return {"error": f"Archivo no encontrado: {file_path}", "file_path": file_path}

        try:
            import librosa
            import numpy as np
        except Exception as exc:  # pragma: no cover - import errors
            return {"error": f"Dependencias faltantes: {exc}", "file_path": file_path}

        try:
            # Load audio using librosa in mono to simplify analysis
            y, sr = librosa.load(file_path, sr=None, mono=True)
            duration = float(librosa.get_duration(y=y, sr=sr))
            audio_info = {"sample_rate": int(sr), "samples": int(len(y))}

            # ---- BPM analysis -------------------------------------------------
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            bpm_analysis = {
                "bpm": float(tempo),
                "confidence": 1.0,  # librosa does not provide confidence
                "method": "librosa.beat.beat_track",
                "tempo_stability": None,
                "beats_detected": int(len(beats)),
                "beats": beats.tolist(),
                "all_estimates": [
                    {"bmp": float(tempo), "confidence": 1.0, "method": "librosa"}
                ],
            }

            # ``auto_hear`` references ``bmp_analysis`` in a few places due to
            # a typo; we therefore provide a mirror of the BPM information
            # under that key to avoid ``KeyError`` exceptions.
            bmp_analysis = {
                "bmp": bpm_analysis["bpm"],
                "confidence": bpm_analysis["confidence"],
                "method": bpm_analysis["method"],
                "tempo_stability": bpm_analysis["tempo_stability"],
                "beats_detected": bpm_analysis["beats_detected"],
                "beats": bpm_analysis["beats"],
                "all_estimates": bpm_analysis["all_estimates"],
            }

            # ---- Key analysis -------------------------------------------------
            chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
            chroma_mean = chroma.mean(axis=1)

            # Simple template matching using major/minor profiles
            major_template = np.array(
                [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
            )
            minor_template = np.array(
                [6.33, 2.68, 3.52, 5.38, 2.6, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]
            )

            note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
            best_key = 0
            best_scale = "major"
            best_score = -float("inf")
            for i in range(12):
                maj_score = np.roll(major_template, i).dot(chroma_mean)
                min_score = np.roll(minor_template, i).dot(chroma_mean)
                if maj_score > best_score:
                    best_score = maj_score
                    best_key = i
                    best_scale = "major"
                if min_score > best_score:
                    best_score = min_score
                    best_key = i
                    best_scale = "minor"

            key_analysis = {
                "key": note_names[best_key],
                "scale": best_scale,
                "confidence": float(best_score / chroma_mean.sum())
                if chroma_mean.sum() > 0
                else 0.0,
                "method": "template_matching",
                "key_stability": None,
                "key_changes_detected": False,
                "chromagram": chroma.tolist(),
            }

            # ---- Silence analysis ---------------------------------------------
            amplitude = np.abs(y)
            # Convert dB threshold to linear amplitude
            threshold_amp = 10 ** (self.silence_threshold / 20.0)
            min_samples = int(self.min_silence_duration * sr)

            silent_mask = amplitude < threshold_amp
            segments: List[Tuple[float, float, float]] = []
            start = None
            for idx, is_silent in enumerate(silent_mask):
                if is_silent and start is None:
                    start = idx
                elif not is_silent and start is not None:
                    if idx - start >= min_samples:
                        segments.append(
                            (start / sr, idx / sr, (idx - start) / sr)
                        )
                    start = None
            if start is not None and len(silent_mask) - start >= min_samples:
                segments.append(
                    (start / sr, len(silent_mask) / sr, (len(silent_mask) - start) / sr)
                )

            total_silence = float(sum(seg[2] for seg in segments))
            silence_analysis = {
                "segments_found": len(segments),
                "segments": segments,
                "total_silence_duration": total_silence,
            }

            # Compose final dictionary
            return {
                "file_path": file_path,
                "duration": duration,
                "audio_info": audio_info,
                "bpm_analysis": bpm_analysis,
                "bmp_analysis": bmp_analysis,
                "key_analysis": key_analysis,
                "silence_analysis": silence_analysis,
            }

        except Exception as exc:  # pragma: no cover - analysis errors
            # Any error during the analysis is captured so the caller can
            # present a friendly message instead of crashing.
            return {"error": str(exc), "file_path": file_path}


def analyze_audio_file(file_path: str, **kwargs: Any) -> Dict[str, Any]:
    """Convenience wrapper around :class:`MusicAnalyzer`.

    Parameters are forwarded to :meth:`MusicAnalyzer.analyze_song`.  Any
    ``KeyError`` or other exception inside ``MusicAnalyzer`` is already
    handled there; this function simply returns the produced dictionary.
    """

    analyzer = MusicAnalyzer()
    if "silence_threshold" in kwargs:
        analyzer.silence_threshold = float(kwargs["silence_threshold"])
    if "min_silence_duration" in kwargs:
        analyzer.min_silence_duration = float(kwargs["min_silence_duration"])

    verbose = bool(kwargs.get("verbose", False))
    return analyzer.analyze_song(file_path, verbose=verbose)


__all__ = ["MusicAnalyzer", "analyze_audio_file"]

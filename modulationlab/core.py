from pathlib import Path
import wave

import numpy as np
from scipy import signal

MAX_BYTES = 32_000_000


def load(path: Path, sample_format: str, sample_rate: float | None) -> tuple[np.ndarray, float]:
    if path.stat().st_size > MAX_BYTES:
        raise ValueError("file exceeds 32 MB")
    if sample_format == "wav-iq":
        with wave.open(str(path), "rb") as stream:
            if stream.getnchannels() != 2 or stream.getsampwidth() != 2 or stream.getcomptype() != "NONE":
                raise ValueError("WAV must be stereo 16-bit PCM IQ")
            rate = stream.getframerate()
            values = np.frombuffer(stream.readframes(stream.getnframes()), dtype="<i2").astype(np.float32) / 32768
        sample_rate = float(rate)
    else:
        if sample_format not in ("cf32le", "cs16le"):
            raise ValueError("unsupported IQ format")
        stride = 8 if sample_format == "cf32le" else 4
        if path.stat().st_size == 0 or path.stat().st_size % stride:
            raise ValueError("empty or truncated IQ file")
        values = np.fromfile(path, dtype="<f4" if sample_format == "cf32le" else "<i2").astype(np.float32)
        if sample_format == "cs16le":
            values /= 32768
    if sample_rate is None or not 1000 <= sample_rate <= 20_000_000:
        raise ValueError("invalid sample rate")
    samples = values[0::2] + 1j * values[1::2]
    if len(samples) < 256 or not np.all(np.isfinite(samples)):
        raise ValueError("insufficient or non-finite IQ")
    return samples, sample_rate


def analyze(samples: np.ndarray, sample_rate: float) -> dict:
    if not 1000 <= sample_rate <= 20_000_000 or len(samples) < 256 or len(samples) > MAX_BYTES // 4:
        raise ValueError("invalid rate or sample count")
    amplitude = np.abs(samples)
    freq = np.angle(samples[1:] * np.conj(samples[:-1])) * sample_rate / (2 * np.pi)
    center_offset = float(np.median(freq))
    amp_cv = float(np.std(amplitude) / max(np.mean(amplitude), 1e-12))
    freq_spread = float(np.percentile(freq, 90) - np.percentile(freq, 10))
    freqs, psd = signal.welch(samples, fs=sample_rate, nperseg=min(1024, len(samples)), return_onesided=False)
    dominant = float(freqs[np.argmax(psd)])
    threshold = float(np.median(amplitude) + np.std(amplitude))
    active = amplitude > threshold
    edges = np.diff(np.pad(active.astype(int), (1, 1)))
    starts, ends = np.where(edges == 1)[0], np.where(edges == -1)[0]
    segments = [{"start_seconds": float(a / sample_rate), "end_seconds": float(b / sample_rate)} for a, b in zip(starts[:100], ends[:100]) if b > a]
    candidate = "undetermined"
    confidence = "low"
    if amp_cv > 0.8 and np.mean(amplitude < np.percentile(amplitude, 25) + 1e-6) > 0.2:
        candidate = "ASK/OOK candidate"
    elif amp_cv < 0.35 and freq_spread > sample_rate * 0.02:
        candidate = "FSK/GFSK or PSK candidate"
    elif amp_cv < 0.35:
        candidate = "constant-envelope PSK/FSK candidate"
    elif amp_cv < 0.8:
        candidate = "QAM/ASK candidate"
    return {"sample_count": int(len(samples)), "sample_rate": sample_rate,
            "frequency_offset_estimate_hz": center_offset, "dominant_psd_offset_hz": dominant,
            "frequency_deviation_indicator_hz": freq_spread / 2,
            "amplitude_mean": float(np.mean(amplitude)), "amplitude_cv": amp_cv,
            "candidate_modulation": candidate, "classification_confidence": confidence,
            "symbol_rate_estimate": None, "segments": segments,
            "psd_offset_hz": freqs.tolist(), "psd_relative_db": (10 * np.log10(np.maximum(psd, 1e-30))).tolist(),
            "interpretation": "heuristic features only; modulation and symbol rate unconfirmed"}

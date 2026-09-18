from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import librosa
import numpy as np
from scipy import signal

FeatureKind = Literal["mfcc", "mel", "psd", "zcr"]


@dataclass(frozen=True)
class AudioConfig:
    sample_rate: int = 44_100
    window_seconds: float = 0.8
    n_mfcc: int = 20
    n_mels: int = 128
    hop_length: int = 512
    n_fft: int = 2048

    @property
    def window_samples(self) -> int:
        return int(round(self.sample_rate * self.window_seconds))


def load_mono_wav(path: str | Path, cfg: AudioConfig) -> np.ndarray:
    """Load and resample to the source-specified 44.1 kHz mono representation."""
    x, _ = librosa.load(path, sr=cfg.sample_rate, mono=True)
    return np.asarray(x, dtype=np.float32)


def amplitude_normalize(x: np.ndarray, eps: float = 1e-8) -> np.ndarray:
    peak = float(np.max(np.abs(x))) if x.size else 0.0
    if peak < eps:
        return x.astype(np.float32, copy=True)
    return (x / peak).astype(np.float32)


def segment_audio(x: np.ndarray, cfg: AudioConfig, drop_last: bool = True) -> list[np.ndarray]:
    """Split into 0.8 s windows, as described in SHIELD8-UAV."""
    n = cfg.window_samples
    chunks = []
    for start in range(0, len(x), n):
        seg = x[start:start+n]
        if len(seg) < n:
            if drop_last:
                break
            seg = np.pad(seg, (0, n-len(seg)))
        chunks.append(seg.astype(np.float32))
    return chunks


def add_awgn(x: np.ndarray, snr_db: float, rng: np.random.Generator | None = None) -> np.ndarray:
    """AWGN augmentation used by the source methodology."""
    rng = rng or np.random.default_rng()
    sig_power = np.mean(np.square(x), dtype=np.float64)
    if sig_power <= 0:
        return x.astype(np.float32, copy=True)
    noise_power = sig_power / (10.0 ** (snr_db / 10.0))
    noise = rng.normal(0.0, np.sqrt(noise_power), size=x.shape)
    return (x + noise).astype(np.float32)


def extract_mfcc(x: np.ndarray, cfg: AudioConfig) -> np.ndarray:
    mfcc = librosa.feature.mfcc(
        y=x,
        sr=cfg.sample_rate,
        n_mfcc=cfg.n_mfcc,
        n_fft=cfg.n_fft,
        hop_length=cfg.hop_length,
    )
    # 1D-F-CNN expects a 1D feature sequence. Mean pooling over time keeps MFCC-20.
    return np.mean(mfcc, axis=1).astype(np.float32)


def extract_mel(x: np.ndarray, cfg: AudioConfig) -> np.ndarray:
    mel = librosa.feature.melspectrogram(
        y=x,
        sr=cfg.sample_rate,
        n_mels=cfg.n_mels,
        n_fft=cfg.n_fft,
        hop_length=cfg.hop_length,
        power=2.0,
    )
    mel_db = librosa.power_to_db(mel, ref=np.max)
    return np.mean(mel_db, axis=1).astype(np.float32)


def extract_psd(x: np.ndarray, cfg: AudioConfig) -> np.ndarray:
    _, pxx = signal.welch(x, fs=cfg.sample_rate, nperseg=min(2048, len(x)))
    return np.log10(np.maximum(pxx, 1e-12)).astype(np.float32)


def extract_zcr(x: np.ndarray, cfg: AudioConfig) -> np.ndarray:
    z = librosa.feature.zero_crossing_rate(
        x, frame_length=cfg.n_fft, hop_length=cfg.hop_length
    )
    return np.mean(z, axis=1).astype(np.float32)


def extract_feature(x: np.ndarray, kind: FeatureKind, cfg: AudioConfig) -> np.ndarray:
    if kind == "mfcc":
        return extract_mfcc(x, cfg)
    if kind == "mel":
        return extract_mel(x, cfg)
    if kind == "psd":
        return extract_psd(x, cfg)
    if kind == "zcr":
        return extract_zcr(x, cfg)
    raise ValueError(f"Unsupported feature kind: {kind}")

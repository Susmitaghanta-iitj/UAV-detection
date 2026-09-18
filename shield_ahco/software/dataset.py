from __future__ import annotations
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import Dataset

from .features import AudioConfig, amplitude_normalize, extract_feature, load_mono_wav, segment_audio


class UAVAudioDataset(Dataset):
    """
    Binary UAV / non-UAV dataset.

    Expected layout:
      root/uav/*.wav
      root/non_uav/*.wav
    """
    def __init__(self, root: str | Path, feature: str = "mfcc", cfg: AudioConfig | None = None):
        self.root = Path(root)
        self.feature = feature
        self.cfg = cfg or AudioConfig()
        self.items: list[tuple[np.ndarray, int, str]] = []

        for class_name, label in [("non_uav", 0), ("uav", 1)]:
            class_dir = self.root / class_name
            for wav in sorted(class_dir.rglob("*.wav")):
                x = amplitude_normalize(load_mono_wav(wav, self.cfg))
                for i, seg in enumerate(segment_audio(x, self.cfg, drop_last=True)):
                    feat = extract_feature(seg, self.feature, self.cfg)
                    self.items.append((feat, label, f"{wav}:{i}"))

        if not self.items:
            raise RuntimeError(f"No WAV segments found under {self.root}")

        lengths = {len(x[0]) for x in self.items}
        if len(lengths) != 1:
            raise RuntimeError(
                f"Feature vectors are not equal length: {sorted(lengths)[:10]}. "
                "Choose a fixed-size feature representation before training."
            )

    def __len__(self):
        return len(self.items)

    def __getitem__(self, idx):
        feat, label, key = self.items[idx]
        # Conv1d input: [channels=1, length]
        x = torch.from_numpy(feat).float().unsqueeze(0)
        y = torch.tensor(label, dtype=torch.long)
        return x, y, key

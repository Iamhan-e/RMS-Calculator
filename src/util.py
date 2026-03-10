# src/utils.py
"""Utility helpers used by the demo script and the notebook."""

from pathlib import Path
from typing import Tuple
import numpy as np
import matplotlib.pyplot as plt


def safe_savefig(fig: plt.Figure, path: Path, dpi: int = 200) -> None:
    """
    Save a Matplotlib figure to ``path`` and create parent directories
    automatically.  Useful in CI or in scripts that run head‑less.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)


def rms_of_signal(signal: np.ndarray) -> float:
    """
    Tiny wrapper that forwards to ``rms_manual`` – kept here so that
    the notebook can import a single function without pulling the whole
    ``rms`` module if it only needs a quick numeric result.
    """
    from .rms import rms_manual

    return rms_manual(signal)


def validate_window_length(samples: int, window_sec: float, fs: float) -> int:
    """
    Convert a window length expressed in seconds to an integer number
    of samples and raise a clear error if the request is impossible.
    Returns the validated ``win_samples``.
    """
    win_samples = int(window_sec * fs)
    if win_samples < 1:
        raise ValueError("Window must contain at least one sample.")
    if win_samples >= samples:
        raise ValueError(
            f"Requested window ({window_sec}s → {win_samples} samples) "
            f"is longer than the available data ({samples} samples)."
        )
    return win_samples

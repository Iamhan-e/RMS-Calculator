# src/rms.py

"""
Core RMS utilities
-----------------

* generate_wave()          – create a clean sinusoid (or any other wave)
* add_noise()              – insert zero‑mean Gaussian noise
* add_dc()                 – add a constant DC bias
* rms_manual()             – √(mean(x²)) – the textbook definition
* rolling_rms()            – moving‑average RMS with a rectangular window
* highpass() (optional)    – simple first‑order HPF to strip DC before RMS
"""

from __future__ import annotations
import numpy as np
from typing import Tuple


def generate_wave(
    pk: float,
    freq: float,
    fs: float,
    duration: float,
    phase: float = 0.0,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Create a sinusoid:  v(t) = pk * sin(2π·freq·t + phase)

    Parameters
    ----------
    pk : float
        Peak amplitude (Vpk).
    freq : float
        Frequency in Hz (e.g. 50 for mains).
    fs : float
        Sampling frequency (samples / s).
    duration : float
        Length of the simulated record (seconds).
    phase : float, optional
        Phase offset in radians, default 0.

    Returns
    -------
    t : np.ndarray
        Time axis (seconds).
    v : np.ndarray
        Voltage samples.
    """
    n_samples = int(fs * duration)
    t = np.arange(n_samples) / fs
    v = pk * np.sin(2 * np.pi * freq * t + phase)
    return t, v


def add_noise(v: np.ndarray, sigma: float, rng: np.random.Generator | None = None) -> np.ndarray:
    """
    Add zero‑mean Gaussian noise.

    Parameters
    ----------
    v : np.ndarray
        Original waveform.
    sigma : float
        Standard deviation of the noise (same units as v).
    rng : np.random.Generator, optional
        Random generator for reproducibility.

    Returns
    -------
    np.ndarray
        Waveform with added noise.
    """
    if rng is None:
        rng = np.random.default_rng()
    noise = rng.normal(0.0, sigma, size=v.shape)
    return v + noise


def add_dc(v: np.ndarray, v_dc: float) -> np.ndarray:
    """Add a constant DC offset."""
    return v + v_dc


def rms_manual(v: np.ndarray) -> float:
    """
    Classic RMS = √(mean(v²)).

    No shortcuts, no external libraries – exactly the definition used in
    power‑meter design textbooks.
    """
    return float(np.sqrt(np.mean(v ** 2)))


def rolling_rms(v: np.ndarray, fs: float, window_sec: float) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute a moving‑average RMS (valid convolution).

    Parameters
    ----------
    v : np.ndarray
        Input waveform.
    fs : float
        Sampling frequency (Hz).
    window_sec : float
        Length of the averaging window, in seconds. Must satisfy
        0 < window_sec < len(v)/fs.

    Returns
    -------
    t_center : np.ndarray
        Time stamps located at the centre of each window.
    rms_vals : np.ndarray
        Rolling RMS values.
    """
    win_samples = int(window_sec * fs)
    if win_samples < 1:
        raise ValueError("Window must contain at least one sample.")
    if win_samples >= len(v):
        raise ValueError(
            f"Window ({window_sec}s → {win_samples} samples) longer "
            f"than the data ({len(v)} samples). Increase the record length."
        )
    # moving‑average of the squared signal (valid mode)
    mean_sq = np.convolve(v ** 2, np.ones(win_samples) / win_samples, mode="valid")
    rms_vals = np.sqrt(mean_sq)

    # centre of each window for a nice time axis
    t_center = (np.arange(len(rms_vals)) + win_samples / 2) / fs
    return t_center, rms_vals


def highpass(v: np.ndarray, fs: float, cutoff: float = 0.5) -> np.ndarray:
    """
    Very small first‑order high‑pass (RC) filter to remove DC before RMS.
    This is optional – you can import it only if you need DC rejection.

    Parameters
    ----------
    v : np.ndarray
        Input waveform (volts).
    fs : float
        Sampling frequency (Hz).
    cutoff : float, optional
        Cut‑off frequency in Hz (default 0.5 Hz, enough to reject mains‑level DC).

    Returns
    -------
    np.ndarray
        Filtered waveform (still same length as input).
    """
    rc = 1.0 / (2 * np.pi * cutoff)
    alpha = rc / (rc + 1.0 / fs)
    y = np.empty_like(v)
    y[0] = v[0]               # assume initial condition = first sample
    for n in range(1, len(v)):
        y[n] = alpha * (y[n - 1] + v[n] - v[n - 1])
    return y




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


def add_harmonic(v: np.ndarray, harmonic_order: int, amplitude_ratio: float, 
                 freq_fundamental: float, fs: float) -> np.ndarray:
    
    t = np.arange(len(v)) / fs
    fundamental_amplitude = (np.max(v) - np.min(v)) / 2
    harmonic_amplitude = amplitude_ratio * fundamental_amplitude
    harmonic = harmonic_amplitude * np.sin(2 * np.pi * harmonic_order * freq_fundamental * t)
    return v + harmonic

def compute_thd(signal: np.ndarray, fs: float, freq_fundamental: float, 
                num_harmonics: int = 10) -> dict:
    
    N = len(signal)
    fft_vals = np.fft.rfft(signal)
    fft_mag = np.abs(fft_vals) / N
    freqs = np.fft.rfftfreq(N, 1/fs)
    
    fundamental_bin = int(freq_fundamental * N / fs)
    fundamental_peak = fft_mag[fundamental_bin] * 2
    fundamental_rms = fundamental_peak / np.sqrt(2)
    
    harmonic_rms_values = []
    harmonic_freqs = []
    
    for h in range(2, num_harmonics + 1):
        harmonic_freq = h * freq_fundamental
        harmonic_bin = int(harmonic_freq * N / fs)
        
        if harmonic_bin < len(fft_mag):
            harmonic_peak = fft_mag[harmonic_bin] * 2
            harmonic_rms = harmonic_peak / np.sqrt(2)
            harmonic_rms_values.append(harmonic_rms)
            harmonic_freqs.append(harmonic_freq)
    
    thd_value = np.sqrt(np.sum(np.array(harmonic_rms_values)**2)) / fundamental_rms
    thd_percent = thd_value * 100
    
    return {
        'thd_percent': thd_percent,
        'harmonic_amplitudes': harmonic_rms_values,
        'frequencies': harmonic_freqs,
        'fundamental_amplitude': fundamental_rms
    }

def verify_parseval(signal: np.ndarray) -> dict:
    """
    Verify Parseval's theorem: Time domain power equals frequency domain power.
    
    Returns dict with 'time_power', 'freq_power', 'relative_error_percent', 'verified'
    """
    time_power = np.mean(signal ** 2)
    
    N = len(signal)
    fft_vals = np.fft.fft(signal)
    freq_power = np.sum(np.abs(fft_vals) ** 2) / (N ** 2)
    
    relative_error = np.abs(time_power - freq_power) / time_power * 100
    
    return {
        'time_power': time_power,
        'freq_power': freq_power,
        'relative_error_percent': relative_error,
        'verified': relative_error < 1e-10
    }

def analyze_snr_impact(v_clean: np.ndarray, noise_levels: np.ndarray) -> dict:
    """
    Analyze how SNR affects RMS measurement accuracy.
    
    Returns dict with 'snr_db', 'rms_error_percent', 'rms_values'
    """
    rms_clean = rms_manual(v_clean)
    results = {'snr_db': [], 'rms_error_percent': [], 'rms_values': []}
    
    for sigma in noise_levels:
        v_noisy = add_noise(v_clean, sigma)
        rms_noisy = rms_manual(v_noisy)
        
        snr = 20 * np.log10(rms_clean / sigma)
        error_percent = (rms_noisy - rms_clean) / rms_clean * 100
        
        results['snr_db'].append(snr)
        results['rms_error_percent'].append(error_percent)
        results['rms_values'].append(rms_noisy)
    
    return results



def detect_frequency(signal: np.ndarray, fs: float, threshold_percent: float = 10) -> float:
    """
    Detect fundamental frequency using zero-crossing detection.
    """
    signal_ac = signal - np.mean(signal)
    
    zero_crossings = []
    for i in range(1, len(signal_ac)):
        if signal_ac[i-1] < 0 and signal_ac[i] >= 0:
            zero_crossings.append(i)
    
    if len(zero_crossings) < 2:
        return 0.0
    
    periods = [zero_crossings[i] - zero_crossings[i-1] for i in range(1, len(zero_crossings))]
    avg_period_samples = np.mean(periods)
    frequency = fs / avg_period_samples
    
    return frequency


def power_quality_analyzer(signal: np.ndarray, fs: float, freq_nominal: float = 50.0) -> dict:
    """
    Complete power quality analyzer - all metrics in one function.
    """
    vrms = rms_manual(signal)
    vpeak = np.max(np.abs(signal))
    dc_offset = np.mean(signal)
    crest_factor = vpeak / vrms if vrms > 0 else 0
    detected_freq = detect_frequency(signal, fs)
    thd_results = compute_thd(signal, fs, freq_nominal)
    
    # Quality assessment
    issues = []
    if thd_results['thd_percent'] > 8:
        issues.append(f"High THD ({thd_results['thd_percent']:.1f}% > 8%)")
    elif thd_results['thd_percent'] > 5:
        issues.append(f"Marginal THD ({thd_results['thd_percent']:.1f}% > 5%)")
    if crest_factor > 1.5:
        issues.append(f"High crest factor ({crest_factor:.2f} > 1.5)")
    if abs(dc_offset) > 0.5:
        issues.append(f"DC offset ({dc_offset:.2f}V)")
    
    quality = "Good power quality" if not issues else "Poor quality: " + "; ".join(issues)
    
    return {
        'vrms': vrms,
        'vpeak': vpeak,
        'crest_factor': crest_factor,
        'frequency_hz': detected_freq,
        'dc_offset_v': dc_offset,
        'thd_percent': thd_results['thd_percent'],
        'quality_assessment': quality
    }

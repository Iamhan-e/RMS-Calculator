# src/__init__.py


from .rms import (
    generate_wave,
    add_noise,
    add_dc,
    rms_manual,
    rolling_rms,
)

__all__ = [
    "generate_wave",
    "add_noise",
    "add_dc",
    "rms_manual",
    "rolling_rms",
]

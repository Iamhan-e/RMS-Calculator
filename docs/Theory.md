# Theory of RMS, Power Quality, and Signal Analysis
*(foundation for the RMS-Calculator repository)*

---

## 1. What is RMS?

For a discrete signal $x[n]$ sampled at $f_s$ Hz, the **Root-Mean-Square** value is:

$$\text{RMS}(x) = \sqrt{\frac{1}{N} \sum_{n=0}^{N-1} x[n]^2}$$

Breaking it down step by step:

- **Square** every sample — converts all values to positive "power" quantities
- **Mean** — average that power across all $N$ samples in the window
- **Square-root** — bring the result back to the original units (volts, amps, etc.)

RMS is the **DC equivalent voltage**: the constant value that would dissipate the same average power in a resistive load as the original AC waveform.

---

## 2. RMS of a Pure Sine Wave

A sinusoid with peak amplitude $V_{pk}$ is defined as:

$$v(t) = V_{pk} \cdot \sin(2\pi f t)$$

Its RMS value has a clean closed form:

$$V_{RMS = \frac{V_{pk}}{\sqrt{2}} \approx 0.707 \cdot V_{pk}}$$

**Why?** Over one full period, the average of $\sin^2$ is exactly $\frac{1}{2}$, so $\sqrt{\text{mean}(\sin^2)} = \frac{1}{\sqrt{2}}$.

**Example — Ethiopian mains supply (230 V RMS):**

$$V_{pk} = 230 \times \sqrt{2} \approx 325 \text{ V}$$

---

## 3. How Noise Affects RMS

Add zero-mean Gaussian noise $n(t) \sim \mathcal{N}(0, \sigma^2)$, independent of the signal:

$$v_{total}(t) = v(t) + n(t)$$

Because the noise and signal are uncorrelated, their cross-term averages to zero. Squaring and integrating gives:

$$\text{RMS}_{total}^2 = V_{RMS}^2 + \sigma^2$$

Taking the square root:

$$\text{RMS_{total} = \sqrt{V_{RMS}^2 + \sigma^2}}$$

**Key insight — noise adds in quadrature.** It always inflates RMS, never reduces it, and the relationship is nonlinear: small noise has very little effect, but large noise dominates.

| Noise std $\sigma$ (relative to $V_{RMS}$) | RMS inflation |
|---|---|
| 1 % | +0.005 % |
| 5 % | +0.12 % |
| 10 % | +0.50 % |
| 50 % | +11.8 % |

---

## 4. How a DC Offset Affects RMS

If a constant bias $V_{DC}$ is present (e.g., from sensor output offset):

$$v_{bias}(t) = v(t) + V_{DC}$$

The DC term contributes permanently to the squared mean:

$$\text{RMS_{bias} = \sqrt{V_{RMS}^2 + V_{DC}^2}}$$

The DC component never cancels, even though it carries no AC power. **Always strip DC before computing RMS** — use a high-pass filter with a cutoff well below mains frequency (e.g., 0.5 Hz).

---

## 5. Rolling (Moving-Average) RMS

A **rolling RMS** tracks power over time by computing RMS within a sliding window of $W$ samples:

$$\text{RMS}_k = \sqrt{\frac{1}{W} \sum_{n=k}^{k+W-1} x[n]^2}$$

In the squared domain, this is a **moving-average (MA) filter** with impulse response:

$$h[n] = \frac{1}{W}, \quad 0 \leq n < W$$

### Frequency Response

The MA filter's magnitude response is:

$$|H(e^{j\omega})| = \frac{1}{W} \left| \frac{\sin(\omega W / 2)}{\sin(\omega / 2)} \right|$$

Its approximate 3 dB cutoff frequency is:

$$f_c \approx \frac{0.443}{T_{win}}$$

where $T_{win} = W / f_s$ is the window duration in seconds.

### Window Length Guide for 50 Hz Mains

| Window | Cutoff $f_c$ | What you see |
|--------|-------------|--------------|
| **5 ms** | ~88 Hz | $f_c > 50$ Hz — the fundamental passes through — RMS **wiggles** sinusoidally |
| **20 ms** (1 period) | ~22 Hz | $f_c < 50$ Hz — fundamental is attenuated — RMS settles to a **flat** true value |
| **50 ms** (2.5 cycles) | ~9 Hz | Extra smooth — ideal for power metering |

**Rule of thumb:** use a window **at least one mains period long** for accurate power averaging. Use a shorter window only when you need fast transient or fault detection and can accept ripple in the RMS reading.

---

## 6. Total Harmonic Distortion (THD)

Real mains waveforms are never pure sinusoids. Non-linear loads — switched-mode power supplies, variable-speed drives, rectifiers — inject energy at integer multiples of the fundamental:

$$v(t) = V_1 \sin(2\pi f_1 t + \phi_1) + \sum_{h=2}^{H} V_h \sin(2\pi h f_1 t + \phi_h)$$

**THD** measures how much of the total signal energy lives in harmonics, relative to the fundamental:

$$\text{THD} = \frac{\sqrt{V_{2,RMS}^2 + V_{3,RMS}^2 + \cdots + V_{H,RMS}^2}}{V_{1,RMS}} \times 100\%$$

### How `compute_thd()` Works

1. Compute the $N$-point FFT of the signal
2. Find the fundamental bin at $f_1$: peak amplitude $\hat{V}_1 = 2|X[k_1]| / N$, RMS value $V_{1,RMS} = \hat{V}_1 / \sqrt{2}$
3. Repeat for each harmonic $h = 2, 3, \ldots, H$
4. Plug into the THD formula

### Industry Thresholds (IEEE 519)

| THD | Assessment |
|-----|------------|
| < 5 % | Good — clean power |
| 5 – 8 % | Marginal — investigate the load |
| > 8 % | Poor — corrective action required |

### Why THD Inflates RMS

The total RMS of a distorted waveform includes all harmonic power:

$$V_{RMS,total} = \sqrt{V_{1,RMS}^2 + V_{2,RMS}^2 + \cdots + V_{H,RMS}^2}$$

A meter reporting total RMS on a distorted waveform is over-counting — it includes harmonic power that heats cables but does no useful work.

---

## 7. Parseval's Theorem

Power is conserved between the time and frequency domains:

$$\frac{1}{N} \sum_{n=0}^{N-1} |x[n]|^2 \;=\; \frac{1}{N^2} \sum_{k=0}^{N-1} |X[k]|^2$$

where $X[k]$ is the $N$-point DFT of $x[n]$.

In plain English: **the total power computed by squaring and averaging the time samples equals the total power computed by summing the squared FFT bins.**

### Why It Matters Here

| Use | How |
|-----|-----|
| **Sanity check** | `verify_parseval()` computes both sides and reports the relative error. Deviation > $10^{-10}$ signals a numerical bug |
| **Power decomposition** | Frequency bins add independently, so you can attribute exactly how much power each harmonic contributes — the mathematical backbone of THD |
| **Regression test** | Run `verify_parseval()` after any DSP change to confirm the pipeline still conserves energy |

---

## 8. SNR and RMS Measurement Accuracy

Signal-to-Noise Ratio in dB:

$$\text{SNR} = 20 \log_{10}\!\left(\frac{V_{RMS}}{\sigma}\right) \text{ dB}$$

From Section 3, the measured RMS of a noisy signal is $\sqrt{V_{RMS}^2 + \sigma^2}$. The **relative RMS error** is:

$$\varepsilon_{RMS} = \frac{\sqrt{V_{RMS}^2 + \sigma^2} \;-\; V_{RMS}}{V_{RMS}} = \sqrt{1 + \frac{1}{\text{SNR}_{linear}^2}} - 1$$

### Accuracy Targets

| SNR | Approx. RMS error |
|-----|-----------|
| 40 dB | < 0.5 % |
| 30 dB | ~1.6 % |
| 20 dB | ~4.9 % |
| 10 dB | ~21 % |

`analyze_snr_impact()` sweeps a range of $\sigma$ values and plots these curves — use it to confirm your ADC and analog front-end meet the accuracy budget before committing to hardware.

---

## 9. Crest Factor

The **crest factor** is the ratio of peak amplitude to RMS:

$$CF = \frac{|v|_{peak}{V_{RMS}}}$$

| Waveform | Crest Factor |
|----------|-------------|
| Pure sine | $\sqrt{2} \approx 1.41$ |
| Square wave | 1.00 |
| Triangle wave | $\sqrt{3} \approx 1.73$ |
| Distorted / spiky | > 1.5 (warning zone) |

A crest factor above **1.5** — flagged by `power_quality_analyzer()` — indicates short, high-amplitude current spikes. This is typical of switched-mode power supplies and stresses wiring and transformers beyond what the RMS figure alone implies.

---

## 10. Fundamental Frequency Detection

`detect_frequency()` estimates $f_1$ using **zero-crossing detection**:

1. Remove DC: $\tilde{x}[n] = x[n] - \bar{x}$
2. Find all sample indices where $\tilde{x}$ crosses zero from negative to positive
3. Average the spacing between consecutive crossings to get the period $T_s$ in samples
4. Return $f = f_s / T_s$

This is computationally cheap and accurate for low-distortion signals. For heavily distorted waveforms, use the FFT-bin approach inside `compute_thd()` instead — the dominant spectral peak reliably locates the fundamental even when zero-crossings are noisy or irregular.

---

## 11. Practical Take-aways for an Energy Monitor

1. **Strip DC before computing RMS.**
   High-pass filter at ~0.5 Hz before calling `rms_manual()`. Even a small bias inflates your reading — especially on low-amplitude current sensors where $V_{DC}$ can be comparable to $V_{RMS}$.

2. **Choose your rolling window carefully.**
   - Power-quality monitoring → window ≥ 1 mains period (~20 ms at 50 Hz)
   - Transient / fault detection → 0.5–1 period (10–20 ms), faster response but ripple is visible

3. **Budget for ADC noise.**
   Quantisation noise with std $\sigma$ inflates measured RMS by $\sqrt{V_{RMS}^2 + \sigma^2}$. Oversampling or a front-end anti-alias filter directly reduces $\sigma$.

4. **Check THD before trusting an RMS reading.**
   High THD means harmonic power is baked into the RMS figure. Use `compute_thd()` to decompose the spectrum, and `power_quality_analyzer()` for a single-call verdict.

5. **Run `verify_parseval()` after any DSP change.**
   It takes milliseconds and confirms the FFT pipeline is conserving energy correctly.

6. **Calibrate against a known source.**
   Compare `rms_manual()` output against a traceable reference. Scale the ADC gain until the library returns exactly $V_{pk} / \sqrt{2}$ for a known sinusoid.

Understanding these relationships ensures that the RMS values reported by the final smart-meter firmware truly reflect the real power drawn from the grid.

---

*End of Theory.md*
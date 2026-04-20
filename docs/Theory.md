# Theory of RMS, Noise, and DC Offset  
*(foundation for the RMS‑Calculator repository)*  

---

## 1. What is RMS?  

For a discrete signal \(x[n]\) sampled at \(f_s\) Hz, the **Root‑Mean‑Square** (RMS) is  

\[
\boxed{\displaystyle
\text{RMS}(x) \;=\; \sqrt{\frac{1}{N}\sum_{n=0}^{N-1} x[n]^{2}}}
\]

- The **square** converts all values to positive power.  
- The **mean** (\(\frac{1}{N}\sum\)) averages that power over the observation window.  
- The **square‑root** brings the quantity back to the original units (volts, amps, …).  

RMS is the **DC voltage that would dissipate the same average power** in a resistive load as the original AC waveform.

---

## 2. RMS of a Pure Sine  

A sinusoid with peak amplitude \(V_{\text{pk}}\)  

\[
v(t)=V_{\text{pk}}\sin(2\pi f t)
\]

has an analytic RMS

\[
\boxed{\displaystyle V_{\text{RMS}} = \frac{V_{\text{pk}}}{\sqrt{2}}}
\]

*Proof*: over one full period the average of \(\sin^{2}\) equals \(\frac12\).

---

## 3. How Noise Affects RMS  

Assume additive zero‑mean Gaussian noise \(n(t)\sim\mathcal N(0,\sigma^{2})\) that is statistically independent of the sine:

\[
v_{\text{total}}(t)=v(t)+n(t)
\]

Because the cross‑term \(\langle v\,n\rangle =0\),

\[
\begin{aligned}
\text{RMS}^{2}_{\text{total}}
  &= \frac{1}{T}\int_0^{T}\bigl(v(t)+n(t)\bigr)^{2}\,dt\\
  &= \underbrace{\frac{1}{T}\int_0^{T}v^{2}(t)\,dt}_{V_{\text{RMS}}^{2}}
     +\underbrace{\frac{1}{T}\int_0^{T}n^{2}(t)\,dt}_{\sigma^{2}} 
\end{aligned}
\]

Hence **noise adds in quadrature**:

\[
\boxed{\displaystyle 
\text{RMS}_{\text{total}} = \sqrt{V_{\text{RMS}}^{2} + \sigma^{2}}}
\]

The larger the noise standard deviation, the larger the measured RMS.

---

## 4. How a DC Offset Affects RMS  

If a constant bias \(V_{\text{DC}}\) is added:

\[
v_{\text{bias}}(t) = v(t) + V_{\text{DC}}
\]

the RMS becomes

\[
\boxed{\displaystyle 
\text{RMS}_{\text{bias}} = \sqrt{V_{\text{RMS}}^{2}+V_{\text{DC}}^{2}}}
\]

The DC term never cancels, so even a modest offset inflates the RMS value.

---

## 5. Rolling (Moving‑Average) RMS  

A **rolling RMS** computes the RMS over a sliding window of length \(T_{\text{win}}\) (or \(W\) samples):

\[
\text{RMS}_{k}
  = \sqrt{\frac{1}{W} \sum_{n=k}^{k+W-1} x[n]^{2}}
\]

In the *squared* domain this is precisely a **moving‑average (MA) filter** with impulse response  

\[
h[n] = \frac{1}{W}\;\;(0\le n < W)
\]

### Frequency response

The magnitude of the MA filter is  

\[
|H(e^{j\omega})|
   = \frac{1}{W}\Bigl|\frac{\sin(\omega W/2)}{\sin(\omega/2)}\Bigr|
\]

Key characteristic:

- **3‑dB cutoff** (approximate)  

\[
f_{\text{c}} \;\approx\; \frac{0.443}{T_{\text{win}}}
\]

- **First null** occurs at \(f = \frac{1}{T_{\text{win}}}\).

### Implications for a 50 Hz mains signal  

| Window length | Approx. cutoff | Relation to 50 Hz |
|---------------|----------------|-------------------|
| **5 ms** (0.005 s) | \(f_{\text{c}}\approx 88\) Hz | Cutoff > 50 Hz → the 50 Hz component passes → the rolling RMS still **wiggles** (looks sinusoidal). |
| **20 ms** (one period) | \(f_{\text{c}}\approx 22\) Hz | Cutoff < 50 Hz → the fundamental is strongly attenuated → the rolling RMS settles to a **flat** value equal to the true RMS. |
| **50 ms** (2.5 cycles) | \(f_{\text{c}}\approx 9\) Hz | Even more smoothing; ideal for power‑measurement where only the DC component of \(x^{2}\) matters. |

**Bottom line:** a window **shorter than one mains period** does **not** remove the AC component; the RMS estimator continues to follow the waveform. Use a window **≥ one period** for an accurate power average, or deliberately use a short window for envelope‑tracking or rapid fault detection (accept the ripple).

---

## 6. Total Harmonic Distortion (THD)

Real-world mains waveforms are never pure sinusoids. Non-linear loads (switched-mode power supplies, variable-speed drives, rectifiers) draw current in pulses, injecting harmonic frequencies at integer multiples of the fundamental:

\[
v(t) = V_1\sin(2\pi f_1 t + \phi_1)
      + \sum_{h=2}^{H} V_h\sin(2\pi h f_1 t + \phi_h)
\]

**Total Harmonic Distortion** quantifies how much of the signal's energy lives in those harmonics relative to the fundamental:

\[
\boxed{\displaystyle
\text{THD} = \frac{\sqrt{\sum_{h=2}^{H} V_{h,\text{RMS}}^{2}}}{V_{1,\text{RMS}}} \times 100\%}
\]

### Computing THD via FFT

`compute_thd()` uses the FFT to extract harmonic amplitudes efficiently:

1. Compute the N-point FFT of the signal.
2. Locate the bin at \(f_1\) and read the peak amplitude \(\hat{V}_1 = 2|X[k_1]|/N\).
3. Convert to RMS: \(V_{1,\text{RMS}} = \hat{V}_1/\sqrt{2}\).
4. Repeat for harmonics \(h = 2, 3, \ldots, H\).
5. Apply the THD formula above.

### Industry Thresholds (IEEE 519)

| THD | Assessment |
|-----|------------|
| < 5 % | Good power quality |
| 5-8 % | Marginal - investigate |
| > 8 % | Poor - corrective action needed |

**Why it matters for RMS:** harmonic content inflates the measured RMS beyond \(V_{1,\text{RMS}}\). The true RMS of a distorted waveform is

\[
V_\text{RMS} = \sqrt{V_{1,\text{RMS}}^{2} + \sum_{h=2}^{H} V_{h,\text{RMS}}^{2}}
\]

A meter that reports RMS without accounting for harmonics is over-reporting useful (fundamental) power.

---

## 7. Parseval's Theorem

Parseval's theorem states that total signal power is conserved between the time and frequency domains:

\[
\boxed{\displaystyle
\frac{1}{N}\sum_{n=0}^{N-1}|x[n]|^{2}
  \;=\;
\frac{1}{N^{2}}\sum_{k=0}^{N-1}|X[k]|^{2}}
\]

where \(X[k]\) is the N-point DFT of \(x[n]\).

### Why it is useful here

- **Sanity check.** `verify_parseval()` computes both sides and reports the relative error. Any deviation larger than \(10^{-10}\) indicates a numerical issue or a bug in the FFT pipeline.
- **Power decomposition.** Because power adds linearly in the frequency domain, you can attribute exactly how much power each harmonic contributes - the basis of the THD calculation above.
- **Regression test.** Any correctly implemented `rms_manual()` on a windowed signal must satisfy Parseval's equality. Run `verify_parseval()` after any change to the DSP chain.

---

## 8. SNR and RMS Measurement Accuracy

The Signal-to-Noise Ratio (SNR) describes how much the signal power dominates the noise power, expressed in dB:

\[
\text{SNR} = 20\log_{10}\!\left(\frac{V_\text{RMS}}{\sigma}\right) \text{ dB}
\]

From Section 3, the measured RMS of a noisy signal is \(\sqrt{V_\text{RMS}^{2}+\sigma^{2}}\). The **relative RMS error** is therefore:

\[
\varepsilon_\text{RMS}
  = \frac{\sqrt{V_\text{RMS}^{2}+\sigma^{2}} - V_\text{RMS}}{V_\text{RMS}}
  = \sqrt{1 + \text{SNR}_\text{linear}^{-2}} - 1
\]

### Practical SNR targets

| SNR | Approx. RMS error |
|-----|-------------------|
| 40 dB | < 0.5 % |
| 30 dB | ~1.6 % |
| 20 dB | ~4.9 % |
| 10 dB | ~21 % |

`analyze_snr_impact()` sweeps a range of \(\sigma\) values and plots these curves, letting you verify your ADC and analog front-end meet the accuracy budget before committing to hardware.

---

## 9. Crest Factor

The **crest factor** (CF) is the ratio of peak to RMS:

\[
\boxed{\displaystyle
\text{CF} = \frac{|v|_\text{peak}}{V_\text{RMS}}}
\]

For a pure sine: \(\text{CF} = \sqrt{2} \approx 1.414\). Deviations from this baseline reveal waveform shape:

| Signal | Crest Factor |
|--------|-------------|
| Pure sine | \(\sqrt{2} \approx 1.41\) |
| Square wave | 1.00 |
| Heavily distorted / peaky | > 1.5 |

A crest factor above **1.5** is flagged by `power_quality_analyzer()` as a warning: short, high-amplitude current spikes are occurring (typical of switched-mode supplies), which stresses wiring and transformers beyond what the RMS figure alone suggests.

---

## 10. Fundamental Frequency Detection

`detect_frequency()` uses **zero-crossing detection** on the AC component of the signal:

1. Remove the DC mean: \(\tilde{x}[n] = x[n] - \bar{x}\).
2. Find all indices where \(\tilde{x}\) crosses zero from negative to positive.
3. Average the spacing between consecutive crossings to estimate the period in samples \(T_s\).
4. Return \(f = f_s / T_s\).

This method is computationally cheap and works well for low-distortion signals. For heavily distorted waveforms, the FFT-bin approach used inside `compute_thd()` is more robust - the dominant peak in the spectrum reliably locates the fundamental even when zero-crossings are noisy.

---

## 11. Practical Take-aways for an Energy Monitor

1. **Strip DC before RMS.** Use `highpass()` (cutoff ~0.5 Hz) to reject sensor bias before calling `rms_manual()`. Even a small offset on a low-amplitude current sensor produces a disproportionate RMS error.

2. **Choose the rolling window wisely:**
   - *Power-quality monitoring*: >= 1 period (~20 ms for 50 Hz).
   - *Transient / fault detection*: 0.5-1 period (10-20 ms) - faster response, modest ripple.

3. **Budget for noise.** If ADC quantisation noise has std \(\sigma\), the RMS is inflated by \(\sqrt{V_\text{RMS}^{2}+\sigma^{2}}\). Oversampling or a front-end anti-alias filter reduces \(\sigma\) directly.

4. **Check THD before trusting RMS.** High THD means the RMS includes harmonic power that may not be doing useful work. Use `compute_thd()` to decompose the measurement and `power_quality_analyzer()` for a single-call verdict.

5. **Verify with Parseval.** After any change to the DSP chain, run `verify_parseval()` as a quick sanity check that power is being preserved correctly through the FFT pipeline.

6. **Calibrate against a known source.** Compare `rms_manual()` output against a traceable reference. Adjust the ADC gain factor until the library matches \(V_\text{pk}/\sqrt{2}\) for a known sinusoid.

Understanding these relationships ensures that the RMS values reported by the final smart-meter firmware truly reflect the real power drawn from the grid.

---

*End of Theory.md*
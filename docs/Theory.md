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

## 6. Practical Take‑aways for an Energy Monitor  

1. **Compute RMS on the AC component only** – strip any DC bias with a high‑pass filter before RMS calculation.  
2. **Choose the rolling window wisely**:  
   - *Power‑quality monitoring*: ≥ 1 period (≈ 20 ms for 50 Hz).  
   - *Transient detection*: 0.5 – 1 period (10–20 ms) gives a fast response with modest ripple.  
3. **Noise budgeting** – if the ADC’s quantisation or front‑end noise has standard deviation \(\sigma\), the measured RMS will be inflated by \(\sqrt{V_{\text{RMS}}^{2} + \sigma^{2}}\). Proper analog filtering or oversampling can reduce \(\sigma\).  
4. **Calibration** – compare the measured RMS of a known reference (e.g., a calibrated 120 V RMS source). Adjust the gain so that the library’s `rms_manual()` matches the theoretical \(V_{\text{pk}}/\sqrt{2}\).  

Understanding these relationships ensures that the RMS values reported by the final smart‑meter firmware truly reflect the real power drawn from the grid.  

---  

*End of Theory.md*  
# StyleTTS-2 Voice Crafting & Audio Engineering Best Practices

This guide details the audio engineering standards, acoustic mechanics, and parameter tuning strategies required to generate the most natural, human-sounding voices with StyleTTS-2.

---

## 1. Reference Audio Acquisition Standards

The acoustic style encoder directly maps the spectral and temporal characteristics of your reference clips into the latent embedding $s \in \mathbb{R}^{128}$. Imperfections in the source audio become permanent traits of the generated voice.

### Recording Checklist

| Factor | Recommended Standard | Why It Matters |
|---|---|---|
| **Duration** | **6 to 12 seconds** (minimum 5s, max 15s) | Shorter clips lack phonetic richness; longer clips introduce stylistic averaging and lose distinctive vocal color. |
| **Acoustic Dryness** | **Dead silent room, zero reverb** | StyleTTS-2 interprets reverb tail as vocal tract resonance, resulting in a hollow, metallic, or distant synthesized voice. |
| **Format** | **24-bit / 48 kHz or 44.1 kHz WAV (Mono)** | Uncompressed linear PCM prevents lossy compression smearing high frequencies (>12 kHz). |
| **Noise Floor** | **< -60 dBFS** | Background air conditioning, PC fans, or electrical hum will be amplified during diffusion sampling. |
| **Microphone Technique** | Cardioid dynamic/condenser with pop filter at **4–6 inches** | Prevents plosive bass thumps (P/B pops) while maintaining proximity effect warmth. |

### Pre-Processing Source Clips in a DAW or Audacity
Before feeding audio to `merge_voices.bat`:
1. **High-Pass Filter:** Apply an 18 dB/octave high-pass filter at **80 Hz** to eliminate sub-bass rumble and handling noise.
2. **De-Essing:** Subtly attenuate harsh sibilance (6 kHz – 9 kHz) to prevent abrasive whistling sounds in the vocoder.
3. **Normalize Peaks:** Peak-normalize the dry vocal to **-1.0 dBFS** with an integrated RMS around **-18 dBFS to -14 dBFS**.
4. **Remove Ambient Silence:** Trim long silences at the beginning and end, leaving roughly 100ms of clean head and tail room.

---

## 2. Strategic Voice Pairing

StyleTTS-2's latent interpolation allows you to combine complementary vocal traits that rarely occur naturally in a single individual.

### Complementary Pairing Profiles

#### A. The Professional Audiobook Narrator
- **Voice A (Warmth & Weight):** Deep baritone or warm alto chest resonance, steady pace, lower pitch foundation.
- **Voice B (Clarity & Dynamics):** Highly articulated voice with crisp consonants, engaging pitch variation, and clear sibilants.
- **Recommended Ratio:** `0.60` Voice A + `0.40` Voice B.

#### B. The Snappy Conversational LLM Assistant
- **Voice A (Approachability):** Mid-range tenor or clear soprano with natural vocal lift.
- **Voice B (Authority & Intelligibility):** Broadcast-style voice with neutral cadence and precise phoneme transitions.
- **Recommended Ratio:** `0.50` Voice A + `0.50` Voice B.

#### C. The Character / Expressive Vocalist
- **Voice A (Distinctive Timbre):** Raspy, airy, or idiosyncratic vocal color.
- **Voice B (Rhythmic Stability):** Highly controlled, metronomic speaker providing prosodic structure.
- **Recommended Ratio:** `0.35` Voice A + `0.65` Voice B (keeps the unique timbre while preventing prosodic instability).

---

## 3. Style Interpolation Mechanics

The style vector $s$ is computed via:
$$s = \text{StyleEncoder}(x_{\text{mel}})$$

When combining two vectors $s_A$ and $s_B$:

### Linear Interpolation (LERP)
$$s_{\text{blend}} = \alpha \cdot s_A + (1 - \alpha) \cdot s_B$$
- Implemented as default in `scripts/merge_voices.py`.
- Works exceptionally well when both vectors lie in the high-density region of the LibriTTS latent manifold.

### Blend Ratio Guide
- **`0.50` (True Median):** Even 50/50 biological cross-breed.
- **`0.70` (Dominant Parent A):** Voice A provides ~75% of recognizable pitch and formants; Voice B adds subtle brightness or cadence polish.
- **`0.30` (Dominant Parent B):** Voice B dominates the timbre; Voice A provides grounding resonance.

> [!TIP]
> Avoid values above `0.90` or below `0.10`—at extreme boundaries, the secondary voice's contribution becomes negligible.

---

## 4. Synthesis Parameter Optimization Matrix

When calling `inference()` or running `synthesize_dialogue.bat`, tune the following hyperparameters:

```
                                  Diffusion Steps
                     5 (Fast)        10 (Balanced)       20–30 (Studio)
                 ┌───────────────┬───────────────────┬──────────────────┐
           High  │ Expressive    │ Natural Live      │ Mastered Drama / │
       (0.4-0.6) │ Chatbot       │ Dialogue          │ Performance      │
Alpha            ├───────────────┼───────────────────┼──────────────────┤
  (Timbre vs     │ Low-latency   │ Recommended       │ High-fidelity    │
   Prosody) Low  │ Voice Clone   │ General Baseline  │ Voice Actor      │
       (0.1-0.3) │ Stream        │ (Default: 0.3)    │ Replication      │
                 └───────────────┴───────────────────┴──────────────────┘
```

### Parameter Breakdown

| Parameter | Recommended Value | Acoustic Effect |
|---|---|---|
| `alpha` ($\alpha$) | `0.25 - 0.35` | **Balances timbre vs. prosody.** Lower values preserve the merged voice's exact reference timbre. Higher values allow the text's predicted inflection to modulate the tone. |
| `beta` ($\beta$) | `0.65 - 0.75` | **Prosody variation.** Controls pitch contours and rhythm changes across phrases. Setting too high (>0.9) can cause erratic pitch; setting too low (<0.4) results in a monotone robot. |
| `diffusion_steps` | `10` (Draft) / `20` (Final) | Controls the iterative denoising process. 10 steps provides a strong signal-to-noise ratio; 20–30 steps completely cleans the noise floor in high frequencies. |
| `embedding_scale` | `1.0` | Classifier-free guidance scale. Values between `1.0` and `1.2` accentuate the unique acoustic traits of the style vector. Values > `1.5` may introduce harsh artifacts. |

---

## 5. Text Preparation & Punctuation Direction

StyleTTS-2 relies on punctuation to compute rhythmic pauses, breath grouping, and phrase boundaries.

### Punctuation Control Rules
1. **Commas (`,`)**: Produces a short, 150–250ms conversational pause with a slight rising or suspended pitch inflection.
2. **Periods (`.`)**: Generates a 350–500ms phrase-final stop with falling intonation.
3. **Ellipses (`...`)**: Introduces a deliberate hesitation or thoughtful elongation of the preceding vowel.
4. **Em-dashes (`—`)**: Produces an abrupt parenthetical pause without downward pitch decay.
5. **Question Marks (`?`)**: Directs the prosody predictor to impart an authentic interrogative upturn.

### Formatting Numbers and Acronyms
The eSpeak-NG phonemizer translates text into IPA phonemes. For optimal pronunciation:
- Spell out ambiguous abbreviations: Use `"Doctor"` instead of `"Dr."`, `"versus"` instead of `"vs."`.
- Format years and phone numbers explicitly: Write `"nineteen ninety-five"` rather than `"1995"`.
- Use hyphenation for acronyms if you want individual letters pronounced: `"A-I"` instead of `"AI"`, `"N-A-S-A"` instead of `"NASA"`.

---

## 6. Long-Form Dialogue Handling

For multi-sentence paragraphs, always use `engine.long_inference()` rather than feeding the entire block to `engine.inference()`.

- **Automatic Sentence Chunking:** `long_inference` uses NLTK's `sent_tokenize` to segment text into natural sentences.
- **Cross-Sentence Style Continuity:** The same merged latent vector $s_{\text{blend}}$ is passed across every sentence chunk, preventing sudden voice changes between paragraphs.
- **Seamless Concatenation:** Generates subtle natural cross-faded pauses between sentences.

This is automatically handled inside [`scripts/synthesize_dialogue.py`](file:///D:/trellis/000.StyleTTS-2/scripts/synthesize_dialogue.py).


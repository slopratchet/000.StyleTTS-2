# StyleTTS-2 Voice Merger & Dialogue System

A localized, self-contained pipeline for neural voice cloning, latent style merging, and dialogue speech synthesis using **StyleTTS-2**.

---

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Quick Start & Batch Files](#quick-start--batch-files)
   - [1. `preprocess_audio.bat`](#1-preprocess_audiobat)
   - [2. `merge_voices.bat`](#2-merge_voicesbat)
   - [3. `synthesize_dialogue.bat`](#3-synthesize_dialoguebat)
   - [4. `run_styletts2.bat`](#4-run_styletts2bat)
3. [Directory Layout](#directory-layout)
4. [Python Scripts & CLI Reference](#python-scripts--cli-reference)
5. [Acoustic Architecture: Latent Style Blending](#acoustic-architecture-latent-style-blending)
6. [Best Practices for Studio-Grade Voices](#best-practices-for-studio-grade-voices)
7. [Integrating into LLM Pipelines](#integrating-into-llm-pipelines)
8. [Troubleshooting & FAQ](#troubleshooting--faq)

---

## Architecture Overview

Traditional voice mixing combines separate audio waveforms, resulting in two people speaking on top of each other. In contrast, **StyleTTS-2** operates on the model's **128-dimensional acoustic style latent space** ($s \in \mathbb{R}^{128}$).

```
Voice A Clip (.wav) ───► [Style Encoder] ───► Style Vector s_A (128-d) ┐
                                                                      ├─► Interpolation: s_blend = α·s_A + (1-α)·s_B
Voice B Clip (.wav) ───► [Style Encoder] ───► Style Vector s_B (128-d) ┘                    │
                                                                                           ▼
                                                                           Frozen Identity Tensor (merged_identity.pt)
                                                                                           │
Dialogue Text ────────► [Text & Phoneme Aligner] ──► [Diffusion Vocoder] ◄─────────────────┘
                                                             │
                                                             ▼
                                                Blended Dialogue Audio (.wav)
```

By extracting the style embeddings from two reference recordings and interpolating them mathematically:
$$s_{\text{blend}} = \alpha \cdot s_A + (1 - \alpha) \cdot s_B$$
the diffusion vocoder synthesizes speech as a **single, organic vocal identity** with a biological vocal tract blending the timbre, resonance, and cadence of both sources.

---

## Quick Start & Batch Files

The repository is equipped with dedicated Windows batch scripts configured to utilize the embedded Python environment and local eSpeak-NG phonemizer out of the box.

### 1. `preprocess_audio.bat`
Automates DSP acoustic hygiene for raw reference audio before voice blending.
- **80 Hz High-Pass Filter:** Strips HVAC and sub-bass microphone handling rumble ($18\text{ dB/octave}$ zero-phase Butterworth).
- **Dynamic De-Esser:** Clamps excessive sibilance ($6\text{ kHz} - 9\text{ kHz}$) to prevent whistling vocoder artifacts.
- **Silence Trimming & Padding:** Strips ambient head/tail silence with energy-based VAD and appends clean $100\text{ ms}$ headroom.
- **Peak Normalization:** Conforms audio to $-1.0\text{ dBFS}$ with integrated RMS auditing.
- **Outputs Produced:** Creates `input/clean_<filename>.wav` for every source clip.

### 2. `merge_voices.bat`
Merges two reference audio clips into a frozen style vector (`merged_identity.pt`) and exports a verification WAV file.

- **Standard Run:** Place two WAV clips at `input/voice_a.wav` and `input/voice_b.wav`, then double-click `merge_voices.bat`.
- **Drag & Drop:** Select two `.wav` files in Windows Explorer and drag them directly onto `merge_voices.bat`.
- **Blend Ratio Prompt:** The script prompts for a ratio between `0.0` and `1.0`:
  - `0.50`: Equal 50/50 balance (recommended starting point).
  - `0.70`: 70% Voice A resonance/cadence, 30% Voice B timbre.
  - `0.30`: 30% Voice A, 70% Voice B.

**Outputs Produced:**
- `output/merged_identity.pt`: The permanent frozen embedding.
- `output/test_blend.wav`: Verification synthesis clip.

---

### 3. `synthesize_dialogue.bat`
Synthesizes speech using the frozen `output/merged_identity.pt` created by the voice merger.

- **Interactive Mode:** Double-click the script. When prompted, type or paste your dialogue and press `Enter`.
- **File-Based Mode:** Place multi-sentence dialogue into `input/dialogue.txt`. When launched, the batch script detects this file and prompts to synthesize it directly.
- **Drag & Drop:** Drag and drop any `.txt` file onto `synthesize_dialogue.bat`.
- **Command Line:** Run `synthesize_dialogue.bat "Your custom dialogue line here"`.

**Outputs Produced:**
- `output/dialogue_YYYYMMDD_HHMMSS.wav`: Timestamped audio recording.
- `output/dialogue_latest.wav`: Convenient fixed filename pointing to the latest take.

---

### 4. `run_styletts2.bat`
The core launcher script that runs the default voice merging pipeline and checks environment integrity.

---

## Directory Layout

```
000.StyleTTS-2/
├── doc/                            # Comprehensive documentation and guides
│   ├── README.md                   # System manual & architecture overview
│   └── Voice_Crafting_Best_Practices.md  # Detailed audio engineering guide
├── espeak-ng/                      # Localized eSpeak-NG binaries and language data
├── input/                          # Input audio references and text prompts
│   ├── dialogue.txt                # Sample/default dialogue text
│   ├── voice_a.wav                 # Reference audio for Voice A
│   └── voice_b.wav                 # Reference audio for Voice B
├── models/                         # Pretrained StyleTTS-2 checkpoints
│   ├── config.yml                  # Model architecture hyperparameters
│   └── epochs_2nd_00020.pth        # LibriTTS multi-speaker weights (~735 MB)
├── output/                         # Synthesis outputs and style tensors
│   ├── dialogue_latest.wav         # Most recent dialogue generation
│   ├── merged_identity.pt          # Frozen style embedding tensor
│   └── test_blend.wav              # Blend verification sample
├── python_embeded/                 # Isolated, self-contained Python 3.12 environment
├── scripts/                        # Automation & inference scripts
│   ├── llm_serving_example.py      # Zero-drift streaming LLM serving template
│   ├── merge_voices.py             # Latent style interpolation & export engine
│   ├── preprocess_audio.py         # DSP pre-processing (HPF, de-esser, silence trim, peak norm)
│   └── synthesize_dialogue.py      # Dialogue synthesizer supporting long-form text
├── merge_voices.bat                # 1-click batch launcher for voice blending
├── preprocess_audio.bat            # 1-click batch launcher for audio DSP pre-processing
├── synthesize_dialogue.bat         # 1-click batch launcher for dialogue synthesis
└── run_styletts2.bat               # Master runner batch file
```

---

## Python Scripts & CLI Reference

All scripts are executed via the embedded interpreter: `python_embeded\python.exe`.

### `scripts/merge_voices.py`
```dos
python_embeded\python.exe scripts\merge_voices.py [OPTIONS]
```
| Parameter | Default | Description |
|---|---|---|
| `--voice-a` | `input/voice_a.wav` | Path to Voice A reference `.wav` |
| `--voice-b` | `input/voice_b.wav` | Path to Voice B reference `.wav` |
| `--ratio` | `0.5` | Interpolation weight: `1.0` = 100% A, `0.0` = 100% B |
| `--output-pt` | `output/merged_identity.pt` | Output file for the frozen identity tensor |
| `--output-wav` | `output/test_blend.wav` | Output file for the test audio take |
| `--test-text` | Sample test sentence | Text spoken for the verification audio |

### `scripts/synthesize_dialogue.py`
```dos
python_embeded\python.exe scripts\synthesize_dialogue.py [OPTIONS]
```
| Parameter | Default | Description |
|---|---|---|
| `--identity` | `output/merged_identity.pt` | Path to frozen style tensor |
| `--text` | `None` | Dialogue string to synthesize directly |
| `--text-file` | `None` | Path to text file containing dialogue |
| `--output` | `output/dialogue_<timestamp>.wav` | Target WAV destination |
| `--diffusion-steps` | `10` | Sampling steps (`5`=fast, `10`=balanced, `20`=studio) |

---

## Acoustic Architecture: Latent Style Blending

StyleTTS-2 separates linguistic content from acoustic style:
1. **Linguistic Representation:** The text input is phonemized with eSpeak-NG and encoded through a fine-tuned PL-BERT transformer into linguistic hidden states.
2. **Style Space Extraction:** The style encoder compresses a reference audio waveform into a dense 128-dimensional embedding $s = [s_{\text{temporal}}, s_{\text{prosodic}}]$.
3. **Diffusion Sampling:** A conditional diffusion model generates mel-spectrogram trajectories conditioned jointly on the linguistic text states and the style vector $s$.
4. **Vocoding:** A HiFi-GAN-style decoder synthesizes the 24kHz raw PCM audio waveform.

Because the style vector is continuous and smooth, linear interpolation between $s_A$ and $s_B$ produces natural vocal intermediate states without robotic timbre or phase cancellation.

---

## Best Practices for Studio-Grade Voices

For maximum fidelity and zero synthesis artifacts:

### 1. Source Reference Audio Standards
- **Duration:** Keep reference clips strictly between **5 and 15 seconds**. Clips under 3 seconds do not provide enough phonetic diversity; clips over 25 seconds introduce stylistic averaging and muddiness.
- **Dryness:** Zero reverb, room echo, or delay. Reflections in the reference audio will be encoded into the latent vector as permanent hollow hollow vocal tract artifacts.
- **Noise Floor:** Ensure clean silence between words. Remove hum, fan noise, microphone hiss, and background music before feeding clips to the merger.
- **Audio Format:** 16-bit or 24-bit PCM WAV (mono). Avoid lossy formats (MP3/AAC/OGG) which introduce spectral compression artifacts above 12 kHz.
- **Vocal Delivery:** Choose takes with natural, confident cadence, consistent microphone distance (3–6 inches with pop filter), and clear articulation. Avoid vocal fry, heavy whispering, or screaming.

### 2. Complementary Pairing
When selecting two voices to blend:
- **Resonance + Articulation:** Pair a voice with deep chest resonance (Voice A) with a voice that exhibits crisp consonant articulation and lively dynamic pacing (Voice B).
- **Pitch Alignment:** Best results occur when pairing voices within compatible pitch ranges (e.g., baritone with tenor, or mezzo-soprano with soprano). Extreme pitch disparities may require adjusting the blend ratio closer to `0.65` / `0.35`.

### 3. Tuning Synthesis Hyperparameters
- **Diffusion Steps:**
  - `5 steps`: Real-time streaming and quick draft tests (~0.2s latency).
  - `10 steps`: Default balanced production setting. Crisp sibilants and natural tone.
  - `20–30 steps`: Studio quality mastering. Maximizes harmonic richness and removes subtle diffusion noise floor.
- **Alpha ($\alpha \approx 0.3$):** Controls the balance between the reference style's timbre and the text-predicted prosody. Lower values (`0.1 - 0.2`) adhere strictly to the reference voice; higher values (`0.4 - 0.6`) introduce more expressive text dynamics.
- **Beta ($\beta \approx 0.7$):** Controls prosody predictor influence. `0.7` produces lifelike emotional inflection.

---

## Integrating into LLM Pipelines

Once `output/merged_identity.pt` is generated, **do not compute reference styles on each turn**. Instead, load the frozen tensor once into memory:

```python
import torch
import soundfile as sf
from styletts2 import tts

# 1. Initialize engine once during application startup
engine = tts.StyleTTS2(
    model_checkpoint_path="models/epochs_2nd_00020.pth",
    config_path="models/config.yml"
)

# 2. Load the frozen merged identity tensor once
cached_style = torch.load("output/merged_identity.pt")

def synthesize_llm_sentence(sentence_text: str, output_path: str):
    """Zero-drift, low-latency synthesis for incoming LLM tokens."""
    audio = engine.inference(
        text=sentence_text,
        ref_s=cached_style,
        diffusion_steps=5,   # Fast streaming
        alpha=0.3,
        beta=0.7
    )
    sf.write(output_path, audio, samplerate=24000)
```

Refer to [`scripts/llm_serving_example.py`](file:///D:/trellis/000.StyleTTS-2/scripts/llm_serving_example.py) for a complete runnable implementation.

---

## Troubleshooting & FAQ

- **Error: `espeak not installed on your system`:**  
  Make sure `PHONEMIZER_ESPEAK_LIBRARY` points to `D:\trellis\000.StyleTTS-2\espeak-ng\libespeak-ng.dll`. Both batch files set this automatically.
- **Error: `Weights only load failed (PyTorch 2.6+)`:**  
  All scripts in `scripts/` include an automatic override (`weights_only=False`) required for loading StyleTTS-2 checkpoints on modern PyTorch versions.
- **Voice sounds muffled or robotic:**  
  Ensure your reference clips are dry and mono. Try increasing diffusion steps to `15` or `20`, and verify that `--ratio` is set between `0.3` and `0.7`.


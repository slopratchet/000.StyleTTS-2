# Self-Contained StyleTTS-2 Local Automation Pipeline

This repository provides a self-contained local automation environment for **StyleTTS 2** (Towards High-Performance Text-to-Speech with Style Diffusion, Adversarial Training, and Large Speech Language Models).

It is optimized for local Windows workstations and low-to-medium VRAM environments (such as the **NVIDIA RTX 2060 6GB**), providing automated batch processing, zero-shot voice cloning, and interactive synthesis.

---

## Key Highlights

- **Human-Level Prosody:** Uses latent style diffusion and SLM adversarial discriminators to produce natural pitch, cadence, and emotion without flat robotic cadences.
- **Zero-Shot Voice Cloning:** Clone target voices using reference audio clips (3–10 seconds) with multi-speaker LibriTTS checkpoints.
- **Low VRAM Consumption:** Requires only 2GB–4GB VRAM during diffusion sampling, comfortably operating on 6GB GPUs (RTX 2060) with fast real-time factor (< 0.1s RTF on CUDA).
- **Automated Worker-Sower Staging:** Automatically detects `.txt` prompts and `.wav` reference clips placed in `input/` and stages finished 24kHz audio in `output/`.

---

## Directory Structure

```
000.StyleTTS-2/
├── run_styletts2.bat                 # One-click Windows interactive launcher
├── README.md                         # Documentation and pipeline reference
├── input/                            # Staging folder for text prompts & reference audio
│   ├── sample_prompt.txt             # Example text prompt
│   └── reference.wav                 # (Optional) Reference voice for zero-shot cloning
├── output/                           # Directory where synthesized .wav files are written
├── models/                           # Downloaded model checkpoints & configs
│   └── LibriTTS/                     # Multi-speaker checkpoints (epochs_2nd_00020.pth, config.yml)
├── scripts/
│   ├── setup_styletts2.py            # Installs PyTorch (CUDA), styletts2, and dependencies
│   ├── fetch_models.py               # Downloads pre-trained weights from Hugging Face
│   ├── inference.py                  # Standalone CLI & interactive synthesis engine
│   └── worker_sower_router.py        # Automated batch router and directory watcher
└── workflows/
    └── styletts2_pipeline_template.json # Generation parameters and pipeline configuration
```

---

## Prerequisites & Hardware

- **Operating System:** Windows 10 or 11 (64-bit).
- **Python:** Python 3.10 is strongly recommended (compatible with PyTorch, TorchAudio, and phonemizers).
- **GPU:** NVIDIA RTX 2060 (6GB VRAM) or higher with CUDA 12.x support (CPU fallback is also supported).

---

## Quickstart

### 1. Launch with Batch Script
Double-click `run_styletts2.bat`.

The launcher will:
1. Detect or create a dedicated Python 3.10 virtual environment (`.venv`).
2. Verify and automatically install missing dependencies.
3. Open the interactive control menu:
   - **[1] Interactive Speech Synthesis:** Type prompts directly in the console.
   - **[2] Process Pending Batch in 'input/':** Convert all `.txt` files in `input/` into `.wav` audio in `output/`.
   - **[3] Start Continuous Worker-Sower Watcher:** Live folder polling for headless generation.
   - **[4] Download / Verify Pre-trained Models:** Fetch Hugging Face checkpoints.
   - **[5] Run / Repair Setup:** Install or reinstall required libraries.

---

## Command Line Usage

### Manual Dependency Setup
```bash
python scripts\setup_styletts2.py
```

### Download Checkpoints
```bash
python scripts\fetch_models.py
```

### Direct Inference
```bash
# Synthesize text using default multi-speaker voice
python scripts\inference.py --text "StyleTTS 2 generates highly expressive speech."

# Zero-shot voice cloning with reference audio
python scripts\inference.py --text "This voice was cloned using a reference clip." --reference_audio "input/reference.wav" --output "output/cloned_sample.wav"

# Interactive CLI mode
python scripts\inference.py --interactive
```

### Batch Worker-Sower Processing
```bash
# Process all pending text files in input/ once
python scripts\worker_sower_router.py

# Keep watching input/ continuously
python scripts\worker_sower_router.py --watch
```

---

## Synthesis Parameters Guide

Adjust parameters via CLI flags or `workflows/styletts2_pipeline_template.json`:

| Parameter | Default | Range | Description |
| :--- | :--- | :--- | :--- |
| **`alpha`** ($\alpha$) | `0.3` | `0.0 - 1.0` | **Timbre / Identity Transfer:** Lower values maintain neutral speaker timbre; higher values transfer more vocal identity from the reference. |
| **`beta`** ($\beta$) | `0.7` | `0.0 - 1.0` | **Prosody / Style Transfer:** Controls prosodic variation, rhythm, and intonation intensity from the style model. |
| **`diffusion_steps`** | `5` | `3 - 15` | Number of diffusion sampling steps. 5 steps provide real-time synthesis; 10 steps give extra refinement. |
| **`embedding_scale`** | `1.0` | `0.5 - 2.0` | Exaggeration factor for speaker embeddings. |
| **`speed`** | `1.0` | `0.5 - 2.0` | Multiplier for speech pace (1.0 = standard speed). |

---

## Zero-Shot Voice Cloning Workflow

1. Place clean reference audio clips (`.wav`, 16-bit or 24-bit, 3–15 seconds, mono) into `input/`.
2. Name the reference `reference.wav` for global use, or name it matching your prompt file (e.g., `chapter1.txt` pairs with `chapter1.wav`).
3. Run `python scripts\worker_sower_router.py` or option `[2]` in `run_styletts2.bat`.
4. The generated voice-cloned audio will be placed in `output/` with matching file names.

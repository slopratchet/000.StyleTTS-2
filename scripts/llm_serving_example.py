import os
import torch

# PyTorch 2.6+ compatibility for StyleTTS2 checkpoint deserialization
_orig_load = torch.load
torch.load = lambda *args, **kwargs: _orig_load(
    *args, **{**({"weights_only": False} if "weights_only" not in kwargs else {}), **kwargs}
)

import soundfile as sf
from styletts2 import tts

REPO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CHECKPOINT_PATH = os.path.join(REPO_DIR, "models", "epochs_2nd_00020.pth")
CONFIG_PATH = os.path.join(REPO_DIR, "models", "config.yml")
IDENTITY_PATH = os.path.join(REPO_DIR, "output", "merged_identity.pt")

# Configure eSpeak NG path and phonemizer library bindings
candidate_paths = [
    r"C:\Program Files\eSpeak NG\libespeak-ng.dll",
    r"C:\Program Files (x86)\eSpeak NG\libespeak-ng.dll",
    os.path.join(REPO_DIR, "espeak-ng", "libespeak-ng.dll"),
]

for candidate in candidate_paths:
    if os.path.exists(candidate):
        os.environ["PHONEMIZER_ESPEAK_PATH"] = candidate
        os.environ["PHONEMIZER_ESPEAK_LIBRARY"] = candidate
        dll_dir = os.path.dirname(candidate)
        if dll_dir not in os.environ.get("PATH", ""):
            os.environ["PATH"] = dll_dir + os.pathsep + os.environ.get("PATH", "")
        if "espeak-ng" in dll_dir.lower():
            os.environ["ESPEAK_DATA_PATH"] = dll_dir
        try:
            from phonemizer.backend.espeak.wrapper import EspeakWrapper
            EspeakWrapper.set_library(candidate)
        except Exception:
            pass
        break

# Initialize engine once
if os.path.exists(CHECKPOINT_PATH) and os.path.exists(CONFIG_PATH):
    engine = tts.StyleTTS2(model_checkpoint_path=CHECKPOINT_PATH, config_path=CONFIG_PATH)
else:
    engine = tts.StyleTTS2()

# Load frozen identity once
if os.path.exists(IDENTITY_PATH):
    cached_style = torch.load(IDENTITY_PATH)
else:
    cached_style = None

def stream_llm_sentence(text_chunk: str, output_filepath: str):
    if cached_style is None:
        raise FileNotFoundError(f"Identity file not found at {IDENTITY_PATH}. Run scripts/merge_voices.py first.")
    audio = engine.inference(
        text=text_chunk,
        ref_s=cached_style,
        diffusion_steps=5,  # Low diffusion steps for low-latency streaming
        alpha=0.3,
        beta=0.7
    )
    sf.write(output_filepath, audio, samplerate=24000)

if __name__ == "__main__":
    if cached_style is not None:
        out_test = os.path.join(REPO_DIR, "output", "llm_sample.wav")
        stream_llm_sentence("Greetings! I am speaking with your custom blended vocal identity.", out_test)
        print(f"[+] LLM pipeline sample saved to: {out_test}")
    else:
        print("[!] Note: merged_identity.pt has not been created yet.")

import os
import sys
import argparse
import datetime
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
DEFAULT_IDENTITY = os.path.join(REPO_DIR, "output", "merged_identity.pt")

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

def main():
    parser = argparse.ArgumentParser(description="Synthesize dialogue speech from a merged voice identity.")
    parser.add_argument("--identity", type=str, default=DEFAULT_IDENTITY,
                        help="Path to the merged style identity (.pt)")
    parser.add_argument("--text", type=str, default=None,
                        help="Dialogue text string to speak")
    parser.add_argument("--text-file", type=str, default=None,
                        help="Path to a text file containing the dialogue")
    parser.add_argument("--output", type=str, default=None,
                        help="Output path for the generated .wav file")
    parser.add_argument("--diffusion-steps", type=int, default=10,
                        help="Diffusion sampling steps (5=fast, 10=balanced, 20=high quality)")
    args = parser.parse_args()

    identity_path = os.path.abspath(args.identity)
    if not os.path.exists(identity_path):
        print(f"[!] Error: Merged identity file not found at: {identity_path}")
        print("[!] Please run 'merge_voices.bat' first to create your merged voice identity.")
        sys.exit(1)

    # Determine dialogue text
    dialogue_text = ""
    if args.text_file and os.path.exists(args.text_file):
        with open(args.text_file, "r", encoding="utf-8") as f:
            dialogue_text = f.read().strip()
    elif args.text:
        dialogue_text = args.text.strip()
    else:
        # Check if default input/dialogue.txt exists
        default_txt = os.path.join(REPO_DIR, "input", "dialogue.txt")
        if os.path.exists(default_txt):
            with open(default_txt, "r", encoding="utf-8") as f:
                content = f.read().strip()
            if content:
                print(f"[*] Found input dialogue file: {default_txt}")
                dialogue_text = content

    if not dialogue_text:
        print("\n=== StyleTTS-2 Dialogue Synthesizer ===")
        print("Type or paste your dialogue text below (press Enter to speak):")
        dialogue_text = input("> ").strip()

    if not dialogue_text:
        print("[!] Error: No dialogue text provided.")
        sys.exit(1)

    # Determine output path
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(os.path.join(REPO_DIR, "output"), exist_ok=True)
    if args.output:
        output_wav = os.path.abspath(args.output)
    else:
        output_wav = os.path.join(REPO_DIR, "output", f"dialogue_{timestamp}.wav")

    latest_wav = os.path.join(REPO_DIR, "output", "dialogue_latest.wav")

    print("\n========================================================")
    print("            StyleTTS-2 Dialogue Synthesizer             ")
    print("========================================================")
    print(f" Identity : {identity_path}")
    print(f" Output   : {output_wav}")
    print(f" Length   : {len(dialogue_text)} characters")
    print("========================================================")
    print(f"Text Preview:\n\"{dialogue_text[:160]}{'...' if len(dialogue_text) > 160 else ''}\"\n")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[*] Running on device: {device.upper()}")

    print("[*] Initializing StyleTTS-2 engine...")
    if os.path.exists(CHECKPOINT_PATH) and os.path.exists(CONFIG_PATH):
        engine = tts.StyleTTS2(model_checkpoint_path=CHECKPOINT_PATH, config_path=CONFIG_PATH)
    else:
        engine = tts.StyleTTS2()

    print("[*] Loading merged style identity tensor...")
    style_tensor = torch.load(identity_path)

    print(f"[*] Synthesizing speech (diffusion steps: {args.diffusion_steps})...")
    # Use long_inference for multi-sentence or standard inference for short lines
    if len(dialogue_text) > 120 or "\n" in dialogue_text or dialogue_text.count(".") > 1:
        audio = engine.long_inference(
            text=dialogue_text,
            ref_s=style_tensor,
            diffusion_steps=args.diffusion_steps,
            alpha=0.3,
            beta=0.7
        )
    else:
        audio = engine.inference(
            text=dialogue_text,
            ref_s=style_tensor,
            diffusion_steps=args.diffusion_steps,
            alpha=0.3,
            beta=0.7
        )

    sf.write(output_wav, audio, samplerate=24000)
    sf.write(latest_wav, audio, samplerate=24000)

    print(f"[+] Dialogue audio successfully generated!")
    print(f"[+] Output: {output_wav}")
    print(f"[+] Latest: {latest_wav}\n")

if __name__ == "__main__":
    main()


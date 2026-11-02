import os
import sys
import argparse
import time
from pathlib import Path

def get_args():
    parser = argparse.ArgumentParser(description="StyleTTS-2 Inference CLI")
    parser.add_argument("--text", type=str, default="", help="Text to synthesize into speech")
    parser.add_argument("--input_file", type=str, default="", help="Path to input text file")
    parser.add_argument("--reference_audio", type=str, default="", help="Path to reference audio (.wav) for zero-shot voice cloning")
    parser.add_argument("--output", type=str, default="", help="Output audio file path (.wav)")
    parser.add_argument("--alpha", type=float, default=0.3, help="Timbre/speaker style diffusion ratio (0.0 to 1.0, default 0.3)")
    parser.add_argument("--beta", type=float, default=0.7, help="Prosody/style transfer intensity (0.0 to 1.0, default 0.7)")
    parser.add_argument("--diffusion_steps", type=int, default=5, help="Diffusion sampling steps (e.g. 5 to 10)")
    parser.add_argument("--embedding_scale", type=float, default=1.0, help="Style embedding scaling factor (default 1.0)")
    parser.add_argument("--speed", type=float, default=1.0, help="Speech rate multiplier (default 1.0)")
    parser.add_argument("--interactive", action="store_true", help="Launch interactive prompt mode")
    return parser.parse_args()

def run_synthesis(text, reference_audio=None, output_path=None, alpha=0.3, beta=0.7, diffusion_steps=5, embedding_scale=1.0, speed=1.0):
    if not text.strip():
        print("[ERROR] No text provided for synthesis.")
        return None

    base_dir = Path(__file__).resolve().parent.parent
    if not output_path:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_path = base_dir / "output" / f"styletts2_{timestamp}.wav"
    else:
        output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"\n[INFERENCE] Synthesizing speech...")
    print(f" - Text: \"{text}\"")
    print(f" - Reference Voice: {reference_audio if reference_audio else 'Default Model Voice'}")
    print(f" - Parameters: alpha={alpha}, beta={beta}, diffusion_steps={diffusion_steps}, speed={speed}")
    print(f" - Target Output: {output_path}")

    start_time = time.time()
    try:
        from styletts2 import tts
        # Initialize StyleTTS2 engine
        engine = tts.StyleTTS2()
        
        # Check reference audio
        target_ref = str(Path(reference_audio).resolve()) if reference_audio and Path(reference_audio).exists() else None
        
        # Perform inference
        engine.inference(
            text=text,
            target_voice_path=target_ref,
            output_wav_file=str(output_path),
            alpha=alpha,
            beta=beta,
            diffusion_steps=diffusion_steps,
            embedding_scale=embedding_scale,
            speed=speed
        )
        duration = time.time() - start_time
        print(f"[SUCCESS] Audio generated in {duration:.2f}s -> {output_path}")
        return output_path
    except ImportError:
        print("[ERROR] 'styletts2' package is not installed. Please run 'scripts/setup_styletts2.py' first.")
        return None
    except Exception as e:
        print(f"[ERROR] Inference failed: {e}")
        return None

def interactive_mode():
    print("===================================================")
    print("      StyleTTS-2 Interactive Voice Synthesizer      ")
    print("===================================================")
    print("Type your text prompt and press Enter. (Type 'quit' or 'exit' to stop)\n")
    
    base_dir = Path(__file__).resolve().parent.parent
    default_ref = base_dir / "input" / "reference.wav"
    ref_audio = str(default_ref) if default_ref.exists() else None
    
    if ref_audio:
        print(f"[INFO] Auto-detected reference voice: {ref_audio}")
    else:
        print("[INFO] No 'input/reference.wav' found. Using default multi-speaker voice style.")

    while True:
        try:
            user_text = input("\nEnter text: ").strip()
            if user_text.lower() in ["quit", "exit", "q"]:
                print("Exiting interactive mode.")
                break
            if not user_text:
                continue
            run_synthesis(text=user_text, reference_audio=ref_audio)
        except (KeyboardInterrupt, EOFError):
            print("\nSession ended.")
            break

def main():
    args = get_args()
    if args.interactive:
        interactive_mode()
        return

    text = args.text
    if args.input_file:
        input_file = Path(args.input_file)
        if input_file.exists():
            text = input_file.read_text(encoding="utf-8").strip()
        else:
            print(f"[ERROR] Input file does not exist: {input_file}")
            sys.exit(1)

    if not text:
        interactive_mode()
        return

    run_synthesis(
        text=text,
        reference_audio=args.reference_audio or None,
        output_path=args.output or None,
        alpha=args.alpha,
        beta=args.beta,
        diffusion_steps=args.diffusion_steps,
        embedding_scale=args.embedding_scale,
        speed=args.speed
    )

if __name__ == "__main__":
    main()


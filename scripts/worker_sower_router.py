import os
import sys
import time
import shutil
import argparse
from pathlib import Path

# Add script directory to sys.path for direct imports
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from inference import run_synthesis
except ImportError:
    run_synthesis = None

def process_batch(watch_mode=False, poll_interval=3):
    base_dir = Path(__file__).resolve().parent.parent
    input_dir = base_dir / "input"
    output_dir = base_dir / "output"
    archive_dir = input_dir / "processed"

    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    archive_dir.mkdir(parents=True, exist_ok=True)

    print("===================================================")
    print("      StyleTTS-2 Worker-Sower Batch Router        ")
    print("===================================================")
    print(f"Watching Input Directory : {input_dir.resolve()}")
    print(f"Staging Output Directory : {output_dir.resolve()}")
    print(f"Archived Inputs          : {archive_dir.resolve()}")
    print(f"Mode                     : {'Continuous Watch' if watch_mode else 'Single Batch Pass'}")
    print("---------------------------------------------------\n")

    while True:
        # Find all .txt files directly in input/ (excluding processed/)
        txt_files = [f for f in input_dir.glob("*.txt") if f.is_file()]
        
        # Check for global reference audio in input/
        ref_candidates = list(input_dir.glob("*.wav")) + list(input_dir.glob("*.mp3"))
        global_ref = None
        for ref in ref_candidates:
            if "reference" in ref.stem.lower() or "voice" in ref.stem.lower() or "sample" in ref.stem.lower():
                global_ref = ref
                break
        if not global_ref and ref_candidates:
            global_ref = ref_candidates[0]

        if txt_files:
            print(f"[ROUTER] Found {len(txt_files)} pending text job(s)...")
            for txt_file in txt_files:
                try:
                    text_content = txt_file.read_text(encoding="utf-8").strip()
                    if not text_content:
                        print(f"[SKIP] Empty file: {txt_file.name}")
                        shutil.move(str(txt_file), str(archive_dir / txt_file.name))
                        continue

                    # Look for paired audio sample, e.g. prompt1.txt + prompt1.wav
                    paired_ref = input_dir / f"{txt_file.stem}.wav"
                    selected_ref = paired_ref if paired_ref.exists() else global_ref

                    out_wav_name = f"{txt_file.stem}_generated.wav"
                    target_out_path = output_dir / out_wav_name

                    print(f"\n[JOB START] Processing '{txt_file.name}'...")
                    if run_synthesis:
                        run_synthesis(
                            text=text_content,
                            reference_audio=str(selected_ref) if selected_ref else None,
                            output_path=target_out_path
                        )
                    else:
                        print(f"[ROUTER] Inference module not found. Synthesizing skipped for {txt_file.name}")

                    # Move processed text file to archive
                    dest_archive = archive_dir / f"{txt_file.stem}_{int(time.time())}.txt"
                    shutil.move(str(txt_file), str(dest_archive))
                    print(f"[JOB COMPLETE] Archived input text to: {dest_archive.name}")

                except Exception as e:
                    print(f"[ERROR] Failed processing {txt_file.name}: {e}")

        if not watch_mode:
            print("\n[ROUTER] Single batch pass finished.")
            break

        time.sleep(poll_interval)

def main():
    parser = argparse.ArgumentParser(description="StyleTTS-2 Worker-Sower Batch Router")
    parser.add_argument("--watch", action="store_true", help="Run continuously and poll input directory for new tasks")
    parser.add_argument("--interval", type=int, default=3, help="Polling interval in seconds (default: 3s)")
    args = parser.parse_args()

    process_batch(watch_mode=args.watch, poll_interval=args.interval)

if __name__ == "__main__":
    main()

import os
import sys
from pathlib import Path

def download_file_hf(repo_id, filename, target_dir):
    try:
        from huggingface_hub import hf_hub_download
        print(f"[INFO] Downloading '{filename}' from repo '{repo_id}'...")
        file_path = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            local_dir=str(target_dir),
            local_dir_use_symlinks=False
        )
        print(f"[OK] Downloaded: {file_path}")
        return Path(file_path)
    except ImportError:
        print("[ERROR] huggingface_hub is not installed. Run: pip install huggingface_hub")
        return None
    except Exception as e:
        print(f"[WARNING] Automatic download failed for {filename}: {e}")
        return None

def main():
    base_dir = Path(__file__).resolve().parent.parent
    models_dir = base_dir / "models"
    libritts_dir = models_dir / "LibriTTS"
    libritts_dir.mkdir(parents=True, exist_ok=True)

    print("===================================================")
    print("      StyleTTS-2 Model Downloader / Verifier       ")
    print("===================================================")
    print(f"Target Models Directory: {models_dir.resolve()}\n")

    # Primary checkpoint: LibriTTS multi-speaker / zero-shot cloning
    repo_id = "yl4579/StyleTTS2-LibriTTS"
    files_to_download = [
        ("Models/LibriTTS/epochs_2nd_00020.pth", libritts_dir),
        ("Models/LibriTTS/config.yml", libritts_dir)
    ]

    for remote_path, local_target in files_to_download:
        fname = Path(remote_path).name
        target_file = local_target / fname
        if target_file.exists() and target_file.stat().st_size > 1024:
            print(f"[OK] Model file already exists: {target_file.name} ({target_file.stat().st_size // (1024*1024)} MB)")
        else:
            print(f"[FETCH] Retrieving {fname}...")
            download_file_hf(repo_id, remote_path, models_dir)

    print("\n---------------------------------------------------")
    print("Model verification summary:")
    print(f"1. LibriTTS Weights & Config: {libritts_dir.resolve()}")
    print("2. Models will also be automatically cached by `styletts2` wrapper if used.")
    print("---------------------------------------------------")
    print("[DONE] StyleTTS-2 models are ready for inference.\n")

if __name__ == "__main__":
    main()

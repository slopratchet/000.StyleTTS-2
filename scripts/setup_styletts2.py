import os
import sys
import subprocess
from pathlib import Path

REQUIRED_PACKAGES = [
    "torch",
    "torchaudio",
    "styletts2",
    "soundfile",
    "librosa",
    "huggingface_hub",
    "scipy",
    "numpy",
    "transformers"
]

def check_cuda():
    try:
        import torch
        cuda_avail = torch.cuda.is_available()
        device_name = torch.cuda.get_device_name(0) if cuda_avail else "CPU only"
        print(f"[INFO] PyTorch CUDA available: {cuda_avail} ({device_name})")
        return cuda_avail
    except ImportError:
        print("[INFO] PyTorch is not yet installed in the current environment.")
        return False

def install_dependencies():
    print("===================================================")
    print("  StyleTTS-2 Setup: Installing Python Dependencies ")
    print("===================================================")
    
    # Upgrade pip first
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    
    # Install PyTorch with CUDA if not present
    try:
        import torch
    except ImportError:
        print("[INFO] Installing PyTorch with CUDA 12.1 support...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install",
            "torch", "torchaudio",
            "--index-url", "https://download.pytorch.org/whl/cu121"
        ])
    
    print("[INFO] Installing core StyleTTS-2 dependencies...")
    for pkg in REQUIRED_PACKAGES:
        print(f"[INFO] Ensuring '{pkg}' is installed...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

def prepare_directories():
    base_dir = Path(__file__).resolve().parent.parent
    dirs = [
        base_dir / "input",
        base_dir / "output",
        base_dir / "models",
        base_dir / "workflows"
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
    print("[INFO] Project directories verified (input, output, models, workflows).")

def main():
    prepare_directories()
    install_dependencies()
    print("\n[INFO] Validating installation...")
    check_cuda()
    print("\n===================================================")
    print(" StyleTTS-2 Setup Completed Successfully!")
    print(" You can now run 'run_styletts2.bat' or inference scripts.")
    print("===================================================")

if __name__ == "__main__":
    main()


import os
import sys
import numpy as np
import soundfile as sf
from scipy import signal

def butter_highpass(cutoff_hz: float, sr: int, order: int = 3):
    """Generates an 18 dB/octave (order=3) Butterworth high-pass filter."""
    nyq = 0.5 * sr
    norm_cutoff = cutoff_hz / nyq
    return signal.butter(order, norm_cutoff, btype="highpass", output="sos")

def butter_bandpass(lowcut: float, highcut: float, sr: int, order: int = 2):
    """Isolates the sibilance frequency band (6 kHz - 9 kHz)."""
    nyq = 0.5 * sr
    low = lowcut / nyq
    high = highcut / nyq
    return signal.butter(order, [low, high], btype="bandpass", output="sos")

def apply_deesser(audio: np.ndarray, sr: int, sibilance_threshold_db: float = -18.0, max_reduction_db: float = 6.0) -> np.ndarray:
    """
    Dynamic de-esser: isolates 6-9 kHz, detects bursts exceeding threshold, 
    and applies proportional attenuation.
    """
    sos_band = butter_bandpass(6000.0, 9000.0, sr, order=2)
    sibilance = signal.sosfiltfilt(sos_band, audio)

    # Calculate moving RMS energy envelope of sibilant frequencies (20ms window)
    window_size = int(sr * 0.02)
    envelope = np.sqrt(np.convolve(sibilance**2, np.ones(window_size) / window_size, mode="same") + 1e-12)
    envelope_db = 20 * np.log10(np.maximum(envelope, 1e-6))

    # Calculate dynamic reduction curve
    overshoot = np.maximum(envelope_db - sibilance_threshold_db, 0.0)
    reduction_db = np.minimum(overshoot * 0.75, max_reduction_db)
    gain_scale = 10 ** (-reduction_db / 20.0)

    # Blend attenuated sibilance back with base audio
    return (audio - sibilance) + (sibilance * gain_scale)

def trim_silence_and_pad(audio: np.ndarray, sr: int, silence_thresh_db: float = -45.0, pad_ms: float = 100.0) -> np.ndarray:
    """Removes ambient head/tail silence and appends exactly pad_ms of clean headroom."""
    frame_len = int(sr * 0.02)
    # Calculate short-term energy profile
    energy = np.sqrt(np.convolve(audio**2, np.ones(frame_len) / frame_len, mode="same") + 1e-12)
    energy_db = 20 * np.log10(np.maximum(energy, 1e-6))

    voiced_indices = np.where(energy_db > silence_thresh_db)[0]
    if len(voiced_indices) == 0:
        return audio  # Fallback if audio is fully silent

    start_idx = max(0, voiced_indices[0] - int(sr * 0.01))
    end_idx = min(len(audio), voiced_indices[-1] + int(sr * 0.01))
    trimmed = audio[start_idx:end_idx]

    # Add 100ms silence padding to head and tail
    pad_samples = int(sr * (pad_ms / 1000.0))
    pad = np.zeros(pad_samples, dtype=audio.dtype)
    return np.concatenate([pad, trimmed, pad])

def normalize_peak(audio: np.ndarray, target_peak_db: float = -1.0) -> np.ndarray:
    """Normalizes the waveform to the target peak dBFS."""
    target_amplitude = 10 ** (target_peak_db / 20.0)
    peak = np.max(np.abs(audio))
    if peak > 0:
        audio = audio * (target_amplitude / peak)
    return audio

def process_file(file_path: str, output_path: str):
    data, sr = sf.read(file_path)

    # Convert multi-channel/stereo to mono
    if data.ndim > 1:
        data = np.mean(data, axis=1)

    # 1. High-Pass Filter: 18 dB/octave (order=3) at 80 Hz
    sos_hp = butter_highpass(80.0, sr, order=3)
    filtered = signal.sosfiltfilt(sos_hp, data)

    # 2. De-Essing (6 kHz - 9 kHz band)
    deessed = apply_deesser(filtered, sr)

    # 3. Trim Silences & apply 100ms head/tail padding
    trimmed = trim_silence_and_pad(deessed, sr, pad_ms=100.0)

    # 4. Normalize Peak to -1.0 dBFS
    conformed = normalize_peak(trimmed, target_peak_db=-1.0)

    # Diagnostic RMS reporting
    rms_db = 20 * np.log10(np.sqrt(np.mean(conformed**2)) + 1e-12)
    peak_db = 20 * np.log10(np.max(np.abs(conformed)) + 1e-12)

    sf.write(output_path, conformed.astype(np.float32), sr)
    print(f"[+] Conformed: {os.path.basename(file_path)} -> Peak: {peak_db:.2f} dBFS | RMS: {rms_db:.2f} dBFS | Output: {os.path.basename(output_path)}")

def main():
    repo_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    input_dir = os.path.join(repo_dir, "input")

    # Support specific files passed via command line / drag-and-drop
    explicit_files = [f for f in sys.argv[1:] if os.path.isfile(f) and f.lower().endswith((".wav", ".flac", ".mp3", ".ogg"))]

    if explicit_files:
        print(f"[*] Processing {len(explicit_files)} explicitly specified audio file(s)...")
        for src in explicit_files:
            dir_name = os.path.dirname(src)
            base_name = os.path.basename(src)
            clean_name = f"clean_{base_name}" if not base_name.startswith("clean_") else base_name
            dst = os.path.join(dir_name, clean_name)
            process_file(src, dst)
        print("[+] Processing complete.")
        return

    raw_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".wav") and not f.startswith("clean_")]
    if not raw_files:
        print("[!] No .wav files found in input/ directory to process.")
        sys.exit(0)

    print(f"[*] Processing {len(raw_files)} audio file(s) in {input_dir}...")
    for filename in raw_files:
        src = os.path.join(input_dir, filename)
        # Prefix cleaned output to avoid overwriting original source files
        dst = os.path.join(input_dir, f"clean_{filename}")
        process_file(src, dst)

    print("[+] All input files pre-processed and ready for StyleTTS-2.")

if __name__ == "__main__":
    main()


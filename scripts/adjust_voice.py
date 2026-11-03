import os
import sys
import argparse
import numpy as np
import soundfile as sf
import pyworld as pw
from scipy.interpolate import interp1d

REPO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def adjust_audio(input_wav: str, output_wav: str, pitch_semitones: float = 0.0, rate_multiplier: float = 1.0):
    """
    Adjusts pitch (semitones) and rate (speed multiplier) using the WORLD vocoder (PyWorld).
    
    Why PyWorld instead of Phase Vocoder (librosa):
      - Phase vocoders cause vertical phase incoherence across STFT bins, creating metallic,
        hollow, phasey 'robotic' artifacts.
      - Librosa pitch_shift shifts formants along with pitch, changing vocal tract geometry.
      - PyWorld decouples fundamental frequency (f0), spectral envelope (formants), and
        aperiodicity (unvoiced noise). It preserves human vocal tract formants and phase
        coherence, resulting in natural, studio-quality speech.
    """
    if not os.path.exists(input_wav):
        print(f"[!] Error: Audio file not found at: {input_wav}")
        sys.exit(1)

    y, sr = sf.read(input_wav)
    if y.ndim > 1:
        y = np.mean(y, axis=1)

    orig_duration = len(y) / sr

    # If no adjustment is requested, pass through cleanly
    if abs(pitch_semitones) < 1e-4 and abs(rate_multiplier - 1.0) < 1e-4:
        print("[*] No pitch or rate adjustment requested (0.0 semitones, 1.0x rate). Passing through...")
        adjusted = np.copy(y)
    else:
        y_f64 = y.astype(np.float64)
        print("[*] Extracting acoustic parameters via WORLD vocoder (Harvest F0, CheapTrick SP, D4C AP)...")
        f0, t = pw.harvest(y_f64, sr, frame_period=5.0)
        sp = pw.cheaptrick(y_f64, f0, t, sr)
        ap = pw.d4c(y_f64, f0, t, sr)

        # 1. Formant-preserving pitch shift
        if abs(pitch_semitones) > 1e-4:
            print(f"[*] Applying formant-preserving pitch shift: {pitch_semitones:+.2f} semitones...")
            pitch_factor = 2.0 ** (pitch_semitones / 12.0)
            f0 = f0 * pitch_factor

        # 2. Artifact-free time stretch (interpolates acoustic trajectories over time)
        if abs(rate_multiplier - 1.0) > 1e-4:
            if rate_multiplier <= 0:
                print("[!] Error: Rate multiplier must be greater than 0.")
                sys.exit(1)
            print(f"[*] Applying time stretch: {rate_multiplier:.2f}x speed...")
            orig_frames = len(f0)
            new_frames = max(1, int(round(orig_frames / rate_multiplier)))
            orig_idx = np.linspace(0, 1, orig_frames)
            new_idx = np.linspace(0, 1, new_frames)

            # Resample F0 contour
            f0 = interp1d(orig_idx, f0, kind="linear", fill_value="extrapolate")(new_idx)
            f0[f0 < 10.0] = 0.0  # Maintain zero for unvoiced consonants

            # Resample Spectral Envelope (vocal tract formants) and Aperiodicity
            sp = interp1d(orig_idx, sp, axis=0, kind="linear", fill_value="extrapolate")(new_idx)
            ap = interp1d(orig_idx, ap, axis=0, kind="linear", fill_value="extrapolate")(new_idx)

        print("[*] Re-synthesizing natural acoustic waveform...")
        adjusted = pw.synthesize(f0, sp, ap, sr)

    # 3. Peak protection ceiling (-1.0 dBFS)
    peak = np.max(np.abs(adjusted))
    target_peak = 10.0 ** (-1.0 / 20.0)  # ~0.891
    if peak > target_peak:
        print("[*] Normalizing peak ceiling to -1.0 dBFS to prevent digital clipping...")
        adjusted = adjusted * (target_peak / peak)

    new_duration = len(adjusted) / sr

    os.makedirs(os.path.dirname(os.path.abspath(output_wav)), exist_ok=True)
    sf.write(output_wav, adjusted.astype(np.float32), sr)

    print("\n========================================================")
    print("         Natural Audio Pitch & Rate Adjustment          ")
    print("========================================================")
    print(f" Source Audio : {input_wav}")
    print(f" Output Audio : {output_wav}")
    print(f" Engine       : WORLD Vocoder (Harvest / CheapTrick / D4C)")
    print(f" Pitch Shift  : {pitch_semitones:+.2f} semitones (Formant-Preserved)")
    print(f" Rate Factor  : {rate_multiplier:.2f}x (Speed: {rate_multiplier * 100:.1f}%)")
    print(f" Duration     : {orig_duration:.2f}s -> {new_duration:.2f}s")
    print(f" Sample Rate  : {sr} Hz")
    print("========================================================")
    print(f"[+] Successfully exported adjusted audio to:\n    {output_wav}\n")

def main():
    parser = argparse.ArgumentParser(description="Adjust pitch (semitones) and rate (speed multiplier) of a WAV file.")
    parser.add_argument("--input", type=str, default=os.path.join(REPO_DIR, "output", "test_blend.wav"),
                        help="Path to input .wav file")
    parser.add_argument("--output", type=str, default=None,
                        help="Path to output .wav file")
    parser.add_argument("--pitch", type=float, default=0.0,
                        help="Pitch adjustment in semitones (e.g. +1.5, -2.0, 0.0)")
    parser.add_argument("--rate", type=float, default=1.0,
                        help="Rate / speed multiplier (e.g. 1.15 for 15%% faster, 0.90 for 10%% slower)")
    args = parser.parse_args()

    input_path = os.path.abspath(args.input)
    if args.output:
        output_path = os.path.abspath(args.output)
    else:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_adjusted{ext}"

    adjust_audio(
        input_wav=input_path,
        output_wav=output_path,
        pitch_semitones=args.pitch,
        rate_multiplier=args.rate
    )

if __name__ == "__main__":
    main()

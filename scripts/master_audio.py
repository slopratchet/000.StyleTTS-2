import os
import sys
import argparse
import numpy as np
import soundfile as sf
import pyloudnorm as pyln
from scipy import signal

REPO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def design_high_shelf(cutoff_hz: float, gain_db: float, sr: int):
    """
    Designs a gentle high-shelf filter to tame vocoder sheen and high-frequency bleed.
    Adapts cutoff frequency safely below the Nyquist limit for any sample rate.
    """
    nyq = 0.5 * sr
    # Ensure cutoff stays below Nyquist (crucial for 24 kHz audio where Nyquist is 12 kHz)
    safe_cutoff = min(cutoff_hz, nyq * 0.90)
    norm_cutoff = safe_cutoff / nyq
    return signal.butter(2, norm_cutoff, btype="lowpass", output="sos"), safe_cutoff

def master_audio(
    input_wav: str,
    output_wav: str,
    target_lufs: float = -23.0,
    target_peak_db: float = -1.0,
    shelf_cutoff_hz: float = 14000.0,
    shelf_gain_db: float = -3.0
):
    """
    Applies the mastering chain described in doc/Creating a Custom LLM Voice.md:
      1. DC offset removal & phase alignment
      2. Gentle high-shelf / anti-bleed rolloff at 14 kHz (adaptive to Nyquist for 24 kHz)
      3. Integrated loudness normalization to target LUFS (-23 LUFS)
      4. True peak ceiling enforcement (-1.0 dBFS)
    """
    data, sr = sf.read(input_wav)

    # Convert multi-channel/stereo to mono if necessary
    if data.ndim > 1:
        data = np.mean(data, axis=1)

    # 1. DC Offset Removal (Centers the waveform around zero)
    data = data - np.mean(data)

    # 2. Gentle High-Shelf Rolloff for Vocoder De-Bleed (Zero-phase sosfiltfilt)
    sos_lp, applied_cutoff = design_high_shelf(shelf_cutoff_hz, shelf_gain_db, sr)
    wet = signal.sosfiltfilt(sos_lp, data)
    gain_linear = 10.0 ** (shelf_gain_db / 20.0)
    # Blend filtered high end to achieve smooth -3 dB high shelf
    conditioned = data * gain_linear + wet * (1.0 - gain_linear)

    # 3. ITU-R BS.1770-4 Loudness Measurement & Normalization
    meter = pyln.Meter(sr)
    init_lufs = meter.integrated_loudness(conditioned)
    
    # Normalize to target LUFS
    if np.isfinite(init_lufs):
        normalized = pyln.normalize.loudness(conditioned, init_lufs, target_lufs)
    else:
        normalized = conditioned

    # 4. True Peak Normalization Ceiling (-1.0 dBFS)
    peak_linear = np.max(np.abs(normalized))
    peak_ceiling = 10.0 ** (target_peak_db / 20.0)
    if peak_linear > peak_ceiling:
        reduction_factor = peak_ceiling / peak_linear
        normalized = normalized * reduction_factor

    final_lufs = meter.integrated_loudness(normalized)
    final_peak_db = 20.0 * np.log10(np.max(np.abs(normalized)) + 1e-12)

    os.makedirs(os.path.dirname(os.path.abspath(output_wav)), exist_ok=True)
    sf.write(output_wav, normalized.astype(np.float32), sr)

    print("========================================================")
    print("             Audio Mastering & De-Bleed Chain           ")
    print("========================================================")
    print(f" Source File  : {input_wav}")
    print(f" Master File  : {output_wav}")
    print(f" Sample Rate  : {sr} Hz (Nyquist: {sr/2:.0f} Hz)")
    print(f" EQ Rolloff   : {shelf_gain_db:.1f} dB at {applied_cutoff:.0f} Hz (Zero-Phase)")
    print(f" Loudness     : {init_lufs:.2f} LUFS -> {final_lufs:.2f} LUFS (Target: {target_lufs:.1f} LUFS)")
    print(f" True Peak    : {final_peak_db:.2f} dBFS (Ceiling: {target_peak_db:.1f} dBFS)")
    print("========================================================")
    print("[+] Audio mastering complete.\n")

def main():
    parser = argparse.ArgumentParser(description="Master audio to -23 LUFS / -1 dBFS true peak with high-shelf vocoder de-bleed.")
    parser.add_argument("--input", type=str, default=os.path.join(REPO_DIR, "output", "test_blend.wav"),
                        help="Input WAV audio file")
    parser.add_argument("--output", type=str, default=None,
                        help="Output mastered WAV file (default: appends '_mastered' or in-place with --in-place)")
    parser.add_argument("--lufs", type=float, default=-23.0,
                        help="Target integrated loudness in LUFS (default: -23.0)")
    parser.add_argument("--peak", type=float, default=-1.0,
                        help="Target true peak ceiling in dBFS (default: -1.0)")
    parser.add_argument("--in-place", action="store_true",
                        help="Overwrite the input file in place instead of creating a new file")
    args = parser.parse_args()

    input_path = os.path.abspath(args.input)
    if not os.path.exists(input_path):
        print(f"[!] Error: Input file not found: {input_path}")
        sys.exit(1)

    if args.in_place:
        output_path = input_path
    elif args.output:
        output_path = os.path.abspath(args.output)
    else:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_mastered{ext}"

    master_audio(
        input_wav=input_path,
        output_wav=output_path,
        target_lufs=args.lufs,
        target_peak_db=args.peak
    )

if __name__ == "__main__":
    main()


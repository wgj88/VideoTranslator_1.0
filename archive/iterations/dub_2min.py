# -*- coding: utf-8 -*-
"""Generate full 2-min Chinese dubbed audio (25 segments)"""
import os, sys, json, subprocess, time

import soundfile as sf
import librosa

sys.path.insert(0, r"E:\VideoTranslator_Project\core_engines")
from clone_dubber import VideoCloneDubber

FFMPEG = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG) + os.pathsep + os.environ["PATH"]

SCRIPT   = r"E:\VideoTranslator_Project\unhinged_tech\UNHINGED_FINAL_506_SCRIPT.json"
SEED_WAV = r"E:\VideoTranslator_Project\unhinged_tech\seeds\ultra_pure_seed.wav"
TEMP     = r"E:\VideoTranslator_Project\temp_factory\dub_2min"
OUTPUT   = r"E:\VideoTranslator_Project\output_final\ZH_2MIN_MASTER.wav"
os.makedirs(TEMP, exist_ok=True)


def smart_steps(text):
    c = len(text)
    if c <= 6:
        return 12
    if c <= 25:
        return 25
    return 50


def vad_trim(raw_path, out_path):
    """VAD-based precise trim + fade-out"""
    y, sr = sf.read(raw_path)
    intervals = librosa.effects.split(y, top_db=22)
    phys_end = intervals[-1][1] / sr if len(intervals) > 0 else len(y) / sr
    fade_start = max(phys_end - 0.05, 0.1)
    subprocess.run([
        FFMPEG, "-y", "-i", raw_path, "-af",
        f"atrim=end={phys_end + 0.1},asetpts=PTS-STARTPTS,afade=t=out:st={fade_start}:d=0.05",
        out_path,
    ], capture_output=True)
    return phys_end


def align_segment(in_path, out_path, phys_dur, quota):
    """Speed-adjust if needed to fit within original time slot"""
    safe = quota - 0.1
    if phys_dur > safe and safe > 0.5:
        tempo = min(1.2, phys_dur / safe)
        actual = phys_dur / tempo
        subprocess.run([
            FFMPEG, "-y", "-i", in_path, "-af",
            f"atrim=end={phys_dur},asetpts=PTS-STARTPTS,atempo={tempo},afade=t=out:st={max(actual-0.05,0.1)}:d=0.05",
            out_path,
        ], capture_output=True)
        return tempo
    return 1.0


def run():
    with open(SCRIPT, "r", encoding="utf-8") as f:
        data = json.load(f)
    segs = [it for it in data if it["start"] < 120]
    print(f"2-minute batch: {len(segs)} segments")
    print(f"Audio span: 0.0s - {segs[-1]['end']:.1f}s\n")

    db = VideoCloneDubber()
    t0 = time.time()
    results = []  # (final_wav_path, start_time)

    for i, item in enumerate(segs):
        zh = item["zh"].strip().strip("、。！？， ")
        ref = SEED_WAV if i == 0 else os.path.join(TEMP, f"clean_{i-1}.wav")
        steps = smart_steps(zh)

        raw_p = os.path.join(TEMP, f"raw_{i}.wav")
        wav = db.model.generate(text=zh, reference_wav_path=ref, inference_timesteps=steps)
        sf.write(raw_p, wav, db.sample_rate)

        clean_p = os.path.join(TEMP, f"clean_{i}.wav")
        phys = vad_trim(raw_p, clean_p)

        quota = item["end"] - item["start"]
        final_p = os.path.join(TEMP, f"final_{i}.wav")
        tempo = align_segment(clean_p, final_p, phys, quota)
        results.append((final_p, item["start"]))

        elapsed = time.time() - t0
        eta = (elapsed / (i + 1)) * (len(segs) - i - 1)
        tempo_tag = f" tempo={tempo:.2f}x" if tempo != 1.0 else ""
        print(f"  [{i+1}/{len(segs)}] {zh} (phys={phys:.2f}s, slot={quota:.1f}s{tempo_tag})  total={elapsed:.0f}s ETA={eta:.0f}s")

    # Mix all segments with adelay alignment
    print(f"\nMixing {len(results)} segments -> {OUTPUT}")
    in_args = []
    delays = []
    for idx, (p, start_t) in enumerate(results):
        in_args.extend(["-i", p])
        delays.append(f"[{idx}:a]adelay={int(start_t*1000)}|{int(start_t*1000)}[a{idx}]")
    mix = "".join(f"[a{k}]" for k in range(len(results))) + f"amix=inputs={len(results)}:duration=longest[aout]"
    subprocess.run(
        [FFMPEG, "-y"] + in_args + [
            "-filter_complex", ";".join(delays) + ";" + mix,
            "-map", "[aout]", "-c:a", "pcm_s16le", OUTPUT,
        ],
        check=True, capture_output=True,
    )

    total = time.time() - t0
    y_out, sr_out = sf.read(OUTPUT)
    print(f"\nDone in {total:.0f}s. Output: {OUTPUT}")
    print(f"Duration: {len(y_out)/sr_out:.1f}s, SampleRate: {sr_out}Hz")


if __name__ == "__main__":
    run()

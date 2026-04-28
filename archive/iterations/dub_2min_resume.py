# -*- coding: utf-8 -*-
"""Resume: align existing clean files + generate remaining segments + mix"""
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

def smart_steps(text):
    c = len(text)
    if c <= 6: return 12
    if c <= 25: return 25
    return 50

def align_segment(in_path, out_path, phys_dur, quota):
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
    else:
        fade_start = max(phys_dur - 0.05, 0.1)
        subprocess.run([
            FFMPEG, "-y", "-i", in_path, "-af",
            f"atrim=end={phys_dur},asetpts=PTS-STARTPTS,afade=t=out:st={fade_start}:d=0.05",
            out_path,
        ], capture_output=True)
        return 1.0

def run():
    with open(SCRIPT, "r", encoding="utf-8") as f:
        data = json.load(f)
    segs = [it for it in data if it["start"] < 120]

    # Step 1: Re-align existing clean files (0-20)
    print("=== Step 1: Re-aligning existing clean files ===")
    t0 = time.time()
    for i in range(21):
        clean_p = os.path.join(TEMP, f"clean_{i}.wav")
        if not os.path.exists(clean_p):
            print(f"  WARNING: clean_{i}.wav missing, skipping")
            continue
        y, sr = sf.read(clean_p)
        phys = len(y) / sr
        quota = segs[i]["end"] - segs[i]["start"]
        final_p = os.path.join(TEMP, f"final_{i}.wav")
        tempo = align_segment(clean_p, final_p, phys, quota)
        tag = f" tempo={tempo:.2f}x" if tempo > 1.01 else ""
        print(f"  [final_{i}] phys={phys:.2f}s, slot={quota:.1f}s{tag}")

    # Step 2: Generate TTS for remaining segments (21-24)
    print("\n=== Step 2: Generating TTS for remaining segments ===")
    db = VideoCloneDubber()
    for i in range(21, len(segs)):
        zh = segs[i]["zh"].strip().strip("、。！？， ")
        if not zh:
            print(f"  [{i+1}/{len(segs)}] SKIP (empty: |{segs[i]['zh'][:20]}|)")
            continue

        ref = SEED_WAV
        for j in range(i-1, -1, -1):
            cp = os.path.join(TEMP, f"clean_{j}.wav")
            if os.path.exists(cp):
                ref = cp
                break

        steps = smart_steps(zh)
        raw_p = os.path.join(TEMP, f"raw_{i}.wav")
        wav = db.model.generate(text=zh, reference_wav_path=ref, inference_timesteps=steps)
        sf.write(raw_p, wav, db.sample_rate)

        clean_p = os.path.join(TEMP, f"clean_{i}.wav")
        y, sr = sf.read(raw_p)
        intervals = librosa.effects.split(y, top_db=22)
        phys = intervals[-1][1] / sr if len(intervals) > 0 else len(y) / sr
        fade_start = max(phys - 0.05, 0.1)
        subprocess.run([
            FFMPEG, "-y", "-i", raw_p, "-af",
            f"atrim=end={phys + 0.1},asetpts=PTS-STARTPTS,afade=t=out:st={fade_start}:d=0.05",
            clean_p,
        ], capture_output=True)

        quota = segs[i]["end"] - segs[i]["start"]
        final_p = os.path.join(TEMP, f"final_{i}.wav")
        tempo = align_segment(clean_p, final_p, phys, quota)
        elapsed = time.time() - t0
        tag = f" tempo={tempo:.2f}x" if tempo > 1.01 else ""
        print(f"  [{i+1}/{len(segs)}] {zh} (phys={phys:.2f}s, slot={quota:.1f}s{tag})  total={elapsed:.0f}s")

    # Step 3: Collect all final files and mix
    print(f"\n=== Step 3: Mixing all segments ===")
    all_final = []
    for i in range(len(segs)):
        zh = segs[i]["zh"].strip().strip("、。！？， ")
        if not zh:
            continue
        fp = os.path.join(TEMP, f"final_{i}.wav")
        if os.path.exists(fp):
            all_final.append((fp, segs[i]["start"]))
        else:
            print(f"  WARNING: final_{i}.wav missing, skipping")

    print(f"Mixing {len(all_final)} segments -> {OUTPUT}")
    in_args = []
    delays = []
    for idx, (p, start_t) in enumerate(all_final):
        in_args.extend(["-i", p])
        delays.append(f"[{idx}:a]adelay={int(start_t*1000)}|{int(start_t*1000)}[a{idx}]")
    mix = "".join(f"[a{k}]" for k in range(len(all_final))) + f"amix=inputs={len(all_final)}:duration=longest[aout]"
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

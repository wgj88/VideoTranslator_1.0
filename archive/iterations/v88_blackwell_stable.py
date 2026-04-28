# -*- coding: utf-8 -*-
import os, sys, json, subprocess, time
import soundfile as sf
import whisper

FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

sys.path.append(r"E:\VideoTranslator_Project")
from clone_dubber import VideoCloneDubber

def run_blackwell_v88_stable():
    print("\n" + "🩺"*10 + " Blackwell 专项：修正版渲染启动 " + "🩺"*10)
    
    script_p = r"E:\VideoTranslator_Project\blackwell_vlog\scripts\V87_PROSODY_SCRIPT.json"
    seed_wav = r"E:\VideoTranslator_Project\unhinged_tech\seeds\ultra_pure_seed.wav"
    output_wav = r"E:\VideoTranslator_Project\output_final\V88_BLACKWELL_VOICE_FIXED.wav"
    
    db = VideoCloneDubber()
    auditor = whisper.load_model("base") # 专项手术刀已就位
    
    with open(script_p, "r", encoding="utf-8") as f: data = json.load(f)
    results = []
    
    for i, item in enumerate(data):
        # 1. 极速生成
        wav = db.model.generate(text=item['zh']+"。", reference_wav_path=seed_wav, inference_timesteps=20)
        raw_p = f"E:\\VideoTranslator_Project\\blackwell_vlog\\final\\v88_raw_{i}.wav"
        sf.write(raw_p, wav, db.sample_rate)
        
        # 2. 纳米级熔断
        res = auditor.transcribe(raw_p, word_timestamps=True)
        semantic_end = res['segments'][-1]['end'] if res['segments'] else 0
        
        # 3. 物理防撞
        next_start = data[i+1]['start'] if i < len(data)-1 else item['end']
        quota = next_start - item['start'] - 0.05
        
        final_p = f"E:\\VideoTranslator_Project\\blackwell_vlog\\final\\v88_fixed_{i}.wav"
        if semantic_end > quota:
            tempo = semantic_end / quota
            print(f"  🚨 [Anti-Collision] 第 {i+1} 段挤压 {tempo:.2f}x")
            cmd = [FFMPEG_BIN, "-y", "-i", raw_p, "-af", f"atrim=end={semantic_end},asetpts=PTS-STARTPTS,atempo={tempo},afade=t=out:st={quota-0.05}:d=0.05", final_p]
        else:
            cmd = [FFMPEG_BIN, "-y", "-i", raw_p, "-af", f"atrim=end={semantic_end},asetpts=PTS-STARTPTS,afade=t=out:st={semantic_end-0.05}:d=0.05", final_p]
        
        subprocess.run(cmd, check=True, capture_output=True)
        results.append((final_p, item['start']))
        print(f"  ✅ [{i+1}/5] {item['zh']}")

    # 4. 缝合
    input_args = []
    filter_parts = []
    for idx, (p, start_t) in enumerate(results):
        input_args.extend(["-i", p])
        filter_parts.append(f"[{idx}:a]adelay={int(start_t*1000)}|{int(start_t*1000)}[a{idx}]")
    
    mix_str = "".join([f"[a{k}]" for k in range(len(results))]) + f"amix=inputs={len(results)}"
    subprocess.run([FFMPEG_BIN, "-y"] + input_args + ["-filter_complex", ";".join(filter_parts) + ";" + mix_str, output_wav], check=True)
    
    print(f"\n🏆 Blackwell 专项首波样音（稳定版）已就绪：{output_wav}")

if __name__ == "__main__":
    run_blackwell_v88_stable()

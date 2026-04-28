# -*- coding: utf-8 -*-
import os, sys, json, subprocess, time
import soundfile as sf
import librosa
import numpy as np

# --- 环境资产锁定 ---
FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

sys.path.append(r"E:\VideoTranslator_Project")
from clone_dubber import VideoCloneDubber

def run_blackwell_v89_glottal_stop():
    print("\n" + "✂️"*10 + " V89 净口版：物理断电引擎启动 " + "✂️"*10)
    
    script_p = r"E:\VideoTranslator_Project\blackwell_vlog\scripts\V87_PROSODY_SCRIPT.json"
    seed_wav = r"E:\VideoTranslator_Project\unhinged_tech\seeds\ultra_pure_seed.wav"
    output_wav = r"E:\VideoTranslator_Project\output_final\V89_BLACKWELL_PURE_SAMPLE.wav"
    
    db = VideoCloneDubber()
    with open(script_p, "r", encoding="utf-8") as f: data = json.load(f)
    results = []
    
    for i, item in enumerate(data):
        # 1. 文本微操：移除句尾标点，防止模型模拟“长叹气”
        clean_text = item['zh'].strip("！。？， ")
        
        # 2. GPU 生成
        wav = db.model.generate(text=clean_text, reference_wav_path=seed_wav, inference_timesteps=20)
        raw_p = f"E:\\VideoTranslator_Project\\blackwell_vlog\\final\\v89_raw_{i}.wav"
        sf.write(raw_p, wav, db.sample_rate)
        
        # 3. 物理断电 (Energy Sentinel)
        # 我们不再相信语义时间戳，直接看波形分贝
        y, sr = librosa.load(raw_p)
        # 找到能量高于 -25dB 的所有片段
        intervals = librosa.effects.split(y, top_db=25)
        if len(intervals) > 0:
            # 物理发音结束的真实位置
            physical_end = intervals[-1][1] / sr
        else:
            physical_end = len(y) / sr

        # 4. 执行硬切割与极速淡出 (5ms)
        final_p = f"E:\\VideoTranslator_Project\\blackwell_vlog\\final\\v89_clean_{i}.wav"
        cmd = [
            FFMPEG_BIN, "-y", "-i", raw_p,
            "-af", f"atrim=end={physical_end + 0.01},asetpts=PTS-STARTPTS,afade=t=out:st={physical_end}:d=0.01",
            final_p
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        
        results.append((final_p, item['start']))
        print(f"  ✅ [{i+1}/5] 已物理切除末端干扰 (End at {physical_end:.3f}s)")

    # 5. 合成
    input_args = []
    filter_parts = []
    for idx, (p, start_t) in enumerate(results):
        input_args.extend(["-i", p])
        filter_parts.append(f"[{idx}:a]adelay={int(start_t*1000)}|{int(start_t*1000)}[a{idx}]")
    
    mix_str = "".join([f"[a{k}]" for k in range(len(results))]) + f"amix=inputs={len(results)}"
    subprocess.run([FFMPEG_BIN, "-y"] + input_args + ["-filter_complex", ";".join(filter_parts) + ";" + mix_str, output_wav], check=True)
    
    print(f"\n🏆 V89 净口版已就绪：{output_wav}")

if __name__ == "__main__":
    run_blackwell_v89_glottal_stop()

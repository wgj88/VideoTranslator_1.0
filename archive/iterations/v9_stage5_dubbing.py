# -*- coding: utf-8 -*-
import os, sys, json, subprocess, re, numpy as np
import librosa, torch, soundfile as sf

# --- 1. 物理环境与 Monkey Patch ---
FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
def ffmpeg_robust_load(path, sr=None, **kwargs):
    target_sr = sr if sr else 44100
    cmd = [FFMPEG_BIN, "-y", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(target_sr), "pipe:1"]
    proc = subprocess.run(cmd, capture_output=True, check=True)
    return np.frombuffer(proc.stdout, dtype=np.float32), target_sr
librosa.load = ffmpeg_robust_load

sys.path.append(r"E:\VideoTranslator_Project")
from clone_dubber import VideoCloneDubber

def run_stage5_multi_dubbing():
    script_path = r"E:\VideoTranslator_Project\separated_audio\v9_final_script_zh_localized.json"
    role_lib_path = r"E:\VideoTranslator_Project\temp_factory\v9_role_library.json"
    temp_dir = r"E:\VideoTranslator_Project\temp_factory\v9_multi_dubs"
    os.makedirs(temp_dir, exist_ok=True)
    
    # 加载数据
    with open(script_path, "r", encoding="utf-8") as f: data = json.load(f)
    with open(role_lib_path, "r", encoding="utf-8") as f: role_lib = json.load(f)
    
    db = VideoCloneDubber()
    print(f"\n[Stage 5] 正在执行全显卡【多角色同步复刻】...")

    # 我们先处理前 10 句进行验证
    for i in range(min(10, len(data))):
        item = data[i]
        text = item.get('zh', '').strip()
        if not text: continue
        
        spk = item['speaker']
        seed = role_lib.get(spk)
        
        if seed:
            print(f"  -> [{spk}] 正在配音: {text[:15]}...")
            # 关键：多角色动态采样引导
            # 强制加上末尾标点
            full_text = text + "。"
            wav = db.model.generate(text=full_text, prompt_wav_path=seed['wav'], prompt_text=seed['text'])
            
            out_p = os.path.join(temp_dir, f"v9_seg_{i}.wav")
            sf.write(out_p, wav, db.sample_rate)
            item['dub_path'] = out_p
            print(f"     ✅ 物理存盘: {os.path.basename(out_p)}")

    # 导出带配音路径的最终 JSON
    with open(script_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"🏆 第五阶段完成：多角色配音片段已就绪。")

if __name__ == "__main__":
    run_stage5_multi_dubbing()

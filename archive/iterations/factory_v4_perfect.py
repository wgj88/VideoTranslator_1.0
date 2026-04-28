# -*- coding: utf-8 -*-
import sys, os, json, subprocess, re, numpy as np
import librosa, torch, soundfile as sf

# --- 物理路径加固 ---
ffmpeg_bin = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
PROJECT_ROOT = r"E:\VideoTranslator_Project"
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output_final")
WAVS_DIR = os.path.join(PROJECT_ROOT, "separated_audio")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(WAVS_DIR, exist_ok=True)

# --- Patch ---
def ffmpeg_robust_load(path, sr=None, **kwargs):
    target_sr = sr if sr else 44100
    cmd = [ffmpeg_bin, "-y", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(target_sr), "pipe:1"]
    proc = subprocess.run(cmd, capture_output=True, check=True)
    return np.frombuffer(proc.stdout, dtype=np.float32), target_sr
librosa.load = ffmpeg_robust_load

sys.path.append(PROJECT_ROOT)
from clone_dubber import VideoCloneDubber
from composer import VideoComposer

# 优质素材：Vlog
v_mp4 = r"E:\VideoTranslator_Project\raw_videos\Vlog ｜ New technology paves way for better life at CICPE.mp4"
v_json = r"E:\VideoTranslator_Project\raw_videos\Vlog ｜ New technology paves way for better life at CICPE_zh.json"
v_vocal = r"C:\Users\Administrator\separated_audio\pure_vocals.wav"

def run_v4_perfect():
    print(f"\n💎 V4.1 终极修正版：物理保存加固启动 💎")
    db = VideoCloneDubber()
    cp = VideoComposer()

    # 1. 深度清洗文本并保存
    with open(v_json, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    for item in data:
        t = item.get('translated_text', '').strip()
        t = re.sub(r'\(.*?\)|\[.*?\]', '', t).strip() # 彻底剔除标签
        if not t.endswith(('。','！','？')): t += "。"
        item['clean_zh'] = t

    # 2. 角色提取 (SPEAKER_00 和 SPEAKER_01 采样)
    # 为演示，我们直接采样前两个角色片段
    seed_wav = os.path.join(WAVS_DIR, "demo_seed.wav")
    subprocess.run([ffmpeg_bin, "-y", "-i", v_vocal, "-ss", "10", "-t", "5", seed_wav], check=True)

    # 3. 核心配音并【物理保存】
    audio_output_dir = os.path.join(PROJECT_ROOT, "raw_videos", "v4_final_wavs")
    os.makedirs(audio_output_dir, exist_ok=True)

    print("\n[V4.1] 正在执行全显卡配音并强制写入磁盘...")
    for i in range(min(10, len(data))):
        item = data[i]
        text = item['clean_zh']
        if len(text) < 2: continue

        print(f"  -> 渲染第 {i} 句: {text[:15]}...")
        # 执行克隆配音
        wav = db.model.generate(text=text, prompt_wav_path=seed_wav, prompt_text=" ")
        
        # 物理保存路径
        out_wav_path = os.path.join(audio_output_dir, f"dub_{i}.wav")
        sf.write(out_wav_path, wav, db.sample_rate)
        
        # 存回 JSON 供合成器使用
        item['dub_path'] = out_wav_path
        
        if os.path.exists(out_wav_path):
            print(f"     ✅ 物理存盘成功: {os.path.basename(out_wav_path)}")

    # 4. 保存 JSON 并合成
    final_json = os.path.join(PROJECT_ROOT, "v4_final_production.json")
    with open(final_json, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("\n[V4.1] 执行最终合成...")
    # 强制调用我们写好的重构版合成引擎
    cp.compose_pure_dub(v_mp4, final_json)
    
    print(f"\n🏆 V4.1 旗舰版大捷！请立刻前往查看 output_final 目录。")

if __name__ == "__main__":
    run_v4_perfect()

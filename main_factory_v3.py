# -*- coding: utf-8 -*-
import sys, os, subprocess, json, re, numpy as np
import librosa
import torch

# --- 🚀 核心补丁：Monkey Patch librosa.load (解决底层库损坏) ---
def ffmpeg_robust_load(path, sr=None, **kwargs):
    ffmpeg_bin = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
    target_sr = sr if sr else 44100
    cmd = [ffmpeg_bin, "-y", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(target_sr), "pipe:1"]
    proc = subprocess.run(cmd, capture_output=True, check=True)
    return np.frombuffer(proc.stdout, dtype=np.float32), target_sr

librosa.load = ffmpeg_robust_load

# --- 引入自研节点 ---
sys.path.append(r"E:\VideoTranslator_Project")
from audio_separator import AudioSeparator
from transcriber import AudioTranscriber
from translator import VideoTranslator
from clone_dubber import VideoCloneDubber
from composer import VideoComposer

# 素材路径
v = r"E:\VideoTranslator_Project\raw_videos\Vlog ｜ New technology paves way for better life at CICPE.mp4"

def run_v3_cloned_factory():
    print(f"\n" + "🔥"*10 + " 自动化工厂 V3.0：音色克隆重制版启动 " + "🔥"*10)
    
    sep = AudioSeparator()
    ts = AudioTranscriber()
    vt = VideoTranslator()
    db = VideoCloneDubber()
    cp = VideoComposer()

    # 1. 纯净剥离
    bgm_wav, vocal_wav = sep.separate(v)
    
    # 2. 听译原文并提取参考文本 (作为克隆引导)
    ref_text = ts.model.transcribe(vocal_wav, language="en")['text'].strip()
    print(f"🎤 音色种子已锁定。引导文本: {ref_text[:30]}...")

    # 3. 听译全篇并执行深度汉化
    raw_json = ts.process(vocal_wav)
    zh_json = vt.translate_json(raw_json)

    # 4. 文本深度净化：移除所有可能被误读的 (Style Tags)
    with open(zh_json, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    for item in data:
        item['translated_text'] = re.sub(r'\(.*?\)', '', item.get('translated_text', ''))
    with open(zh_json, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # 5. 执行全篇克隆配音 (前 10 句)
    print("\n[V3.0] 正在执行全篇音色同步渲染...")
    db.process_json_cloning(zh_json, vocal_wav, ref_text, limit=10)
    
    # 6. 最终合成 (使用修正后的时间轴引擎)
    final_out = cp.compose_pure_dub(v, zh_json)
    
    if final_out:
        print(f"\n🎊 终极定论版本已产出：{final_out}")

if __name__ == "__main__":
    run_v3_cloned_factory()

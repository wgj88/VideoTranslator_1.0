# -*- coding: utf-8 -*-
import sys, os, subprocess, json, numpy as np
import librosa
import torch

# --- 🚀 核心手术：Monkey Patch librosa.load ---
def ffmpeg_robust_load(path, sr=None, **kwargs):
    """
    不依赖 soundfile 的超级音频读取器
    """
    ffmpeg_bin = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
    target_sr = sr if sr else 44100
    
    # 将任何音频转为 raw pcm
    cmd = [
        ffmpeg_bin, "-y", "-i", path,
        "-f", "f32le", "-ac", "1", "-ar", str(target_sr), "pipe:1"
    ]
    proc = subprocess.run(cmd, capture_output=True, check=True)
    audio = np.frombuffer(proc.stdout, dtype=np.float32)
    return audio, target_sr

# 实施手术：将 librosa 的加载函数替换为我的
print("[Patch] 正在为 librosa 实施 FFmpeg 紧急手术...")
librosa.load = ffmpeg_robust_load

# --- 启动正常流程 ---
sys.path.append(r"E:\VideoTranslator_Project")
from audio_separator import AudioSeparator
from transcriber import AudioTranscriber
from translator import VideoTranslator
from clone_dubber import VideoCloneDubber
from composer import VideoComposer

v = r"E:\VideoTranslator_Project\raw_videos\Vlog ｜ New technology paves way for better life at CICPE.mp4"

def start_patched_remake():
    print(f"\n[SURGERY_SUCCESS] 正在通过补丁模式进行全净空汉化...")
    
    sep = AudioSeparator()
    ts = AudioTranscriber()
    vt = VideoTranslator()
    db = VideoCloneDubber()
    cp = VideoComposer()

    # 1. 剥离
    bgm_wav, vocal_wav = sep.separate(v)
    
    # 2. 听译与翻译
    raw_json = ts.process(vocal_wav)
    zh_json = vt.translate_json(raw_json)
    
    # 3. 全篇克隆配音 (此时 VoxCPM 会调用我们的补丁版 librosa.load)
    print("\n[V2.0] 正在执行全篇克隆渲染...")
    ready_json = db.process_json_cloning(zh_json, vocal_wav, "reference", limit=10)
    
    # 4. 合成
    cp.compose(v, ready_json, bgm_wav)
    print(f"\n🏆 补丁模式大捷！作品已生成。")

if __name__ == "__main__":
    start_patched_remake()

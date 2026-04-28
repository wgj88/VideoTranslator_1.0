# -*- coding: utf-8 -*-
import sys, os, subprocess, json, re, numpy as np
import librosa, torch

# --- Monkey Patch ---
def ffmpeg_robust_load(path, sr=None, **kwargs):
    ffmpeg_bin = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
    target_sr = sr if sr else 44100
    cmd = [ffmpeg_bin, "-y", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(target_sr), "pipe:1"]
    proc = subprocess.run(cmd, capture_output=True, check=True)
    return np.frombuffer(proc.stdout, dtype=np.float32), target_sr
librosa.load = ffmpeg_robust_load

sys.path.append(r"E:\VideoTranslator_Project")
from audio_separator import AudioSeparator
from transcriber import AudioTranscriber
from translator import VideoTranslator
from clone_dubber import VideoCloneDubber
from composer import VideoComposer

v = r"E:\VideoTranslator_Project\raw_videos\Vlog ｜ New technology paves way for better life at CICPE.mp4"

def start_stable_remake():
    print(f"\n[STABLE_VERSION] 正在执行稳定版【跨语言克隆】重制...")
    
    sep = AudioSeparator()
    ts = AudioTranscriber()
    vt = VideoTranslator()
    db = VideoCloneDubber()
    cp = VideoComposer()

    # 1. 物理剥离
    bgm_wav, vocal_wav = sep.separate(v)
    
    # 2. 截取极简音色种子 (3秒纯净人声)
    ffmpeg_bin = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
    short_ref = os.path.join(os.path.dirname(vocal_wav), "short_ref.wav")
    subprocess.run([ffmpeg_bin, "-y", "-i", vocal_wav, "-ss", "10", "-t", "3", short_ref], check=True, capture_output=True)

    # 3. 听译与翻译
    raw_json = ts.process(vocal_wav)
    zh_json = vt.translate_json(raw_json)

    # 4. 文本深度净化（强力闭合标点）
    with open(zh_json, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    for item in data:
        t = item.get('translated_text', '').strip()
        t = re.sub(r'\(.*?\)', '', t) # 移除标签
        if not t.endswith(('。', '！', '？')): t += "。"
        item['translated_text'] = t
    with open(zh_json, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # 5. 克隆配音 (参考文本置空，提高跨语言稳定性)
    print("\n[V3.1] 正在执行【空参考文本】克隆渲染...")
    db.process_json_cloning(zh_json, short_ref, "", limit=10)
    
    # 6. 合成 (调用正确的函数名)
    cp.compose_pure_dub(v, zh_json)
    print(f"\n🏆 稳定版大捷！请查看 PURE_CHINESE 作品。")

if __name__ == "__main__":
    start_stable_remake()

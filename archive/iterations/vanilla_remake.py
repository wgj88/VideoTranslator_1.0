# -*- coding: utf-8 -*-
import sys, os, subprocess, json, re, numpy as np
import librosa, torch

# --- Patch ---
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
from dubber import VideoDubber
from composer import VideoComposer

v = r"E:\VideoTranslator_Project\raw_videos\Vlog ｜ New technology paves way for better life at CICPE.mp4"
j = r"E:\VideoTranslator_Project\raw_videos\Vlog ｜ New technology paves way for better life at CICPE_zh.json"

def run_vanilla_clean():
    print(f"\n[V3.2] 正在打造【标准原声 + 全净空】样板...")
    
    sep = AudioSeparator()
    db = VideoDubber() # 使用默认 Dubber (无克隆)
    cp = VideoComposer()

    # 1. 物理剥离 (获取纯 BGM)
    bgm_wav, _ = sep.separate(v)

    # 2. 文本净化
    with open(j, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    
    for item in data:
        t = item.get('translated_text', '').strip()
        t = re.sub(r'\(.*?\)', '', t) # 剔除所有英文标签
        if t and not t.endswith(('。', '！', '？')): t += "。"
        item['translated_text'] = t

    # 3. 渲染前六句 (默认音色)
    print("\n[V3.2] 正在渲染标准中文配音片段...")
    db.process_json(j, limit=6)
    
    # 4. 合成：纯 BGM + 默认配音 (0% 英文干扰)
    print("\n[V3.2] 执行最终混音...")
    # 修改 composer.py 逻辑以支持传入自定义背景音
    output_path = os.path.join(cp.output_dir, "VANILLA_CLEAN_SAMPLE.mp4")
    
    import ffmpeg
    v_stream = ffmpeg.input(v).video
    delayed_streams = []
    for i in range(6):
        item = data[i]
        if 'dub_path' in item and os.path.exists(item['dub_path']):
            delay = int(item['start'] * 1000)
            delayed_streams.append(ffmpeg.input(item['dub_path']).audio.filter('adelay', f"{delay}|{delay}"))
    
    # 混合背景音乐和中文配音
    full_dub = ffmpeg.filter(delayed_streams, 'amix', inputs=len(delayed_streams))
    bg_audio = ffmpeg.input(bgm_wav).audio.filter('volume', 0.5) # BGM 适中
    mixed = ffmpeg.filter([bg_audio, full_dub], 'amix', inputs=2, duration='first')
    
    (
        ffmpeg.output(v_stream, mixed, output_path, vcodec='h264_nvenc', acodec='aac')
        .overwrite_output().run(capture_stdout=True, capture_stderr=True)
    )
    print(f"\n🏆 V3.2 样板打造成功！\n文件路径: {output_path}")

if __name__ == "__main__":
    run_vanilla_clean()

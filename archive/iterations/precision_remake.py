# -*- coding: utf-8 -*-
import sys, os, subprocess, json, re, numpy as np
import librosa, torch, soundfile as sf

# --- 1. 环境加固 (物理路径) ---
ffmpeg_bin = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"

def ffmpeg_robust_load(path, sr=None, **kwargs):
    target_sr = sr if sr else 16000 # 降采样到 16k 提高稳定性
    cmd = [ffmpeg_bin, "-y", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(target_sr), "pipe:1"]
    proc = subprocess.run(cmd, capture_output=True, check=True)
    return np.frombuffer(proc.stdout, dtype=np.float32), target_sr
librosa.load = ffmpeg_robust_load

sys.path.append(r"E:\VideoTranslator_Project")
from dubber import VideoDubber

v_json = r"E:\VideoTranslator_Project\raw_videos\Vlog ｜ New technology paves way for better life at CICPE_zh.json"

def run_precision_factory():
    print(f"\n🚀 正在启动【硬核物理对齐】重制系统...")
    
    db = VideoDubber()
    with open(v_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    audio_segments = []
    # 演示：处理前 5 句，确保每一句都完美
    for i in range(5):
        item = data[i]
        # 1. 文本极度净化
        text = re.sub(r'\(.*?\)|\[.*?\]', '', item.get('translated_text', '')).strip()
        if not text.endswith('。'): text += "。"
        
        print(f"  -> 正在高清渲染第 {i} 句: {text}")
        
        # 2. 生成配音 (使用标准默认音色，排除克隆干扰)
        wav = db.model.generate(text=text)
        
        # 3. 物理对齐：创建一个带有正确延迟的临时文件
        temp_seg = f"E:\\VideoTranslator_Project\\raw_videos\\precision_seg_{i}.wav"
        sf.write(temp_seg, wav, db.sample_rate)
        
        # 使用 FFmpeg 的 adelay 将其推到准确位置
        delay_ms = int(item['start'] * 1000)
        aligned_seg = f"E:\\VideoTranslator_Project\\raw_videos\\aligned_seg_{i}.wav"
        cmd = [ffmpeg_bin, "-y", "-i", temp_seg, "-af", f"adelay={delay_ms}|{delay_ms}", aligned_seg]
        subprocess.run(cmd, check=True, capture_output=True)
        audio_segments.append(aligned_seg)

    # 4. 终极物理混合：将所有对齐后的片段通过 FFmpeg amix 合并
    print("\n[Final] 正在执行多轨物理合并...")
    output_wav = r"E:\VideoTranslator_Project\output_final\PRECISION_AUDITION_TRACK.wav"
    
    input_args = []
    for seg in audio_segments:
        input_args.extend(["-i", seg])
    
    # 构造 amix 命令
    # 注意：这里我们使用 volume=N 来补偿 amix 自动缩小的音量
    filter_str = f"amix=inputs={len(audio_segments)}:duration=longest,volume={len(audio_segments)}"
    cmd = [ffmpeg_bin, "-y"] + input_args + ["-filter_complex", filter_str, output_wav]
    subprocess.run(cmd, check=True)

    print(f"\n🏆 物理对齐音轨已产出：{output_wav}")
    print(f"提示：这个音轨不含背景音，只有中文配音。请听听是否还堆叠，以及中文是否清晰。")

if __name__ == "__main__":
    run_precision_factory()

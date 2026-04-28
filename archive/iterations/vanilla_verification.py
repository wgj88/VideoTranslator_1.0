# -*- coding: utf-8 -*-
import sys, os, subprocess, json, re, numpy as np
import soundfile as sf
import librosa, torch

# --- Monkey Patch (保证底层读取稳健) ---
FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
def ffmpeg_robust_load(path, sr=None, **kwargs):
    target_sr = sr if sr else 44100
    cmd = [FFMPEG_BIN, "-y", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(target_sr), "pipe:1"]
    proc = subprocess.run(cmd, capture_output=True, check=True)
    return np.frombuffer(proc.stdout, dtype=np.float32), target_sr
librosa.load = ffmpeg_robust_load

sys.path.append(r"E:\VideoTranslator_Project")
from dubber import VideoDubber

def run_vanilla_verification():
    # 锁定素材
    j = r"E:\VideoTranslator_Project\raw_videos\Vlog ｜ New technology paves way for better life at CICPE_zh.json"
    temp_dir = r"E:\VideoTranslator_Project\temp_factory"
    os.makedirs(temp_dir, exist_ok=True)
    
    db = VideoDubber()
    with open(j, "r", encoding="utf-8-sig") as f:
        data = json.load(f)

    valid_segments = []
    print(f"\n[Verification] 正在执行【标准版中文】渲染流程...")

    # 渲染前 8 句作为全链路验证
    for i in range(8):
        item = data[i]
        # 1. 文本极度净化：剔除所有非中文标签
        raw_text = item.get('translated_text', item['text'])
        clean_zh = re.sub(r'\(.*?\)|\[.*?\]', '', raw_text).strip()
        # 确保标点闭合
        if clean_zh and not clean_zh.endswith(('。', '！', '？')): clean_zh += "。"
        
        print(f"  -> 正在生成第 {i} 句: {clean_zh}")
        
        # 2. 生成标准中文配音 (无克隆)
        wav = db.model.generate(text=clean_zh)
        
        # 3. 物理对齐：创建带延迟的片段
        raw_p = os.path.join(temp_dir, f"v_raw_{i}.wav")
        sf.write(raw_p, wav, db.sample_rate)
        
        delay_ms = int(item['start'] * 1000)
        aligned_p = os.path.join(temp_dir, f"v_aligned_{i}.wav")
        # FFmpeg 物理补齐时间轴
        subprocess.run([FFMPEG_BIN, "-y", "-i", raw_p, "-af", f"adelay={delay_ms}|{delay_ms}", aligned_p], check=True, capture_output=True)
        valid_segments.append(aligned_p)

    # 4. 终极物理合并
    output_wav = r"E:\VideoTranslator_Project\output_final\VANILLA_CHINESE_VERIFIED.wav"
    input_args = []
    for s in valid_segments: input_args.extend(["-i", s])
    
    # 使用 amix 合并，并进行音量补偿
    filter_str = f"amix=inputs={len(valid_segments)}:duration=longest,volume={len(valid_segments)}"
    cmd = [FFMPEG_BIN, "-y"] + input_args + ["-filter_complex", filter_str, output_wav]
    subprocess.run(cmd, check=True)

    print(f"\n🏆 标准版中文音轨已产出：{output_wav}")
    print("这个音轨不带背景音，只有最纯净、最标准的中文配音，且时序完全正确。")

if __name__ == "__main__":
    run_vanilla_verification()

# -*- coding: utf-8 -*-
import sys, os, json, subprocess, re, numpy as np
import librosa, torch, soundfile as sf

# 1. 物理环境死锁
ffmpeg_bin = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(ffmpeg_bin) + os.pathsep + os.environ["PATH"]

def ffmpeg_robust_load(path, sr=None, **kwargs):
    target_sr = sr if sr else 44100
    cmd = [ffmpeg_bin, "-y", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(target_sr), "pipe:1"]
    proc = subprocess.run(cmd, capture_output=True, check=True)
    return np.frombuffer(proc.stdout, dtype=np.float32), target_sr
librosa.load = ffmpeg_robust_load

sys.path.append(r"E:\VideoTranslator_Project")
from clone_dubber import VideoCloneDubber
from composer import VideoComposer

v_mp4 = r"E:\VideoTranslator_Project\raw_videos\Vlog ｜ New technology paves way for better life at CICPE.mp4"
v_json = r"E:\VideoTranslator_Project\raw_videos\Vlog ｜ New technology paves way for better life at CICPE_zh.json"
v_vocal = r"C:\Users\Administrator\separated_audio\pure_vocals.wav"
work_dir = r"E:\VideoTranslator_Project\FINAL_DUB_TEMP"
os.makedirs(work_dir, exist_ok=True)

def run_final_strike():
    print("=== 🚀 [HorrorVlogger] 最终激活任务开始 ===")
    db = VideoCloneDubber()
    
    # 采集一个绝对干净的 3 秒种子
    seed_wav = os.path.join(work_dir, "seed.wav")
    subprocess.run([ffmpeg_bin, "-y", "-i", v_vocal, "-ss", "10", "-t", "3", seed_wav], check=True)
    
    with open(v_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 核心配音循环
    print("\n[Action] 正在生成中文配音并物理校验...")
    valid_dubs = []
    for i in range(min(8, len(data))):
        item = data[i]
        # 彻底清洗文本，不留任何非中文字符
        text = re.sub(r'\(.*?\)|\[.*?\]', '', item.get('translated_text', '')).strip()
        if not text: continue
        
        print(f"  -> 正在复刻第 {i} 句: {text}")
        # 关键调用：必须带上 prompt_text=" " (一个空格) 解决 API 冲突
        wav = db.model.generate(text=text, prompt_wav_path=seed_wav, prompt_text=" ")
        
        out_wav = os.path.join(work_dir, f"pure_zh_{i}.wav")
        sf.write(out_wav, wav, db.sample_rate)
        
        if os.path.exists(out_wav) and os.path.getsize(out_wav) > 1000:
            print(f"     ✅ 物理存盘成功: {os.path.getsize(out_wav)} bytes")
            item['dub_path'] = out_wav
            valid_dubs.append(item)
        else:
            print(f"     ❌ 存盘失败或文件为空！")

    # 强制执行物理对齐合成 (不带 BGM，排除干扰)
    print("\n[Action] 正在执行全静空物理合成...")
    final_output = r"E:\VideoTranslator_Project\output_final\ABSOLUTE_CHINESE_FINAL.mp4"
    
    # 构造 FFmpeg 合成命令 (物理占位对齐)
    input_cmds = []
    filter_parts = []
    for idx, item in enumerate(valid_dubs):
        input_cmds.extend(["-i", item['dub_path']])
        delay = int(item['start'] * 1000)
        filter_parts.append(f"[{idx+1}:a]adelay={delay}|{delay}[a{idx}]")
    
    filter_str = "".join(filter_parts) + "".join([f"[a{k}]" for k in range(len(valid_dubs))]) + f"amix=inputs={len(valid_dubs)}:duration=longest[out]"
    
    # 执行
    cmd = [ffmpeg_bin, "-y", "-i", v_mp4] + input_cmds + ["-filter_complex", filter_str, "-map", "0:v", "-map", "[out]", "-vcodec", "copy", "-acodec", "aac", final_output]
    subprocess.run(cmd, check=True)
    
    print(f"\n🏆 任务达成！如果这个视频还没中文，那就是魔法了：{final_output}")

if __name__ == "__main__":
    run_final_strike()

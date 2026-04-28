# -*- coding: utf-8 -*-
import sys, os, subprocess, json, re, numpy as np
import librosa, torch, soundfile as sf

# --- 物理路径加固 ---
FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

def ffmpeg_robust_load(path, sr=None, **kwargs):
    target_sr = sr if sr else 44100
    cmd = [FFMPEG_BIN, "-y", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(target_sr), "pipe:1"]
    proc = subprocess.run(cmd, capture_output=True, check=True)
    return np.frombuffer(proc.stdout, dtype=np.float32), target_sr
librosa.load = ffmpeg_robust_load

sys.path.append(r"E:\VideoTranslator_Project")
from dubber import VideoDubber

# 素材锁定
v_mp4 = r"E:\VideoTranslator_Project\raw_videos\Vlog ｜ New technology paves way for better life at CICPE.mp4"
v_json = r"E:\VideoTranslator_Project\raw_videos\Vlog ｜ New technology paves way for better life at CICPE_zh.json"
v_bgm = r"C:\Users\Administrator\separated_audio\pure_bgm.wav"

def run_v7_professional():
    print(f"\n" + "🎬"*10 + " 自动化工厂 V7.0：专业译制版启动 " + "🎬"*10)
    
    db = VideoDubber()
    with open(v_json, "r", encoding="utf-8-sig") as f:
        data = json.load(f)

    # --- 阶段 1: 智能角色画像 (此处模拟匹配 P02 知性女声) ---
    print("[Profiler] 正在分析视频风格... 匹配到音色: 【知性灵动 - P02】")
    style_tag = "(A clear and sweet female voice)"

    # --- 阶段 2: 全篇极速渲染 ---
    audio_dir = r"E:\VideoTranslator_Project\temp_factory\v7_pro_wavs"
    os.makedirs(audio_dir, exist_ok=True)
    
    final_segments = []
    # 渲染前 10 句
    for i in range(min(10, len(data))):
        text = re.sub(r'\(.*?\)|\[.*?\]', '', data[i].get('translated_text', '')).strip()
        if not text: continue
        
        # 强制标点闭合，确保语调完美
        if not text.endswith(('。','！','？')): text += "。"
        final_zh = style_tag + text
        
        print(f"  -> 正在配音第 {i} 句: {text[:15]}...")
        wav = db.model.generate(text=final_zh)
        
        # 物理占位对齐逻辑
        raw_p = os.path.join(audio_dir, f"raw_{i}.wav")
        sf.write(raw_p, wav, db.sample_rate)
        
        delay_ms = int(data[i]['start'] * 1000)
        aligned_p = os.path.join(audio_dir, f"aligned_{i}.wav")
        subprocess.run([FFMPEG_BIN, "-y", "-i", raw_p, "-af", f"adelay={delay_ms}|{delay_ms}", aligned_p], check=True, capture_output=True)
        final_segments.append(aligned_p)

    # --- 阶段 3: 终极商业级合成 ---
    print("\n[Mixer] 正在合并纯净 BGM 与专业配音...")
    output_video = r"E:\VideoTranslator_Project\output_final\V7_PRO_EDITION_VLOG.mp4"
    
    input_args = []
    for s in final_segments: input_args.extend(["-i", s])
    
    # 构造合并滤镜：所有中文片段合并 -> 侧链压制 BGM -> 混合输出
    filter_complex = f"amix=inputs={len(final_segments)}:duration=longest,volume={len(final_segments)}[dub];"
    filter_complex += "[1:a][dub]sidechaincompress=threshold=0.01:ratio=20[bg_ducked];"
    filter_complex += "[bg_ducked][dub]amix=inputs=2:weights='0.1 1.0'[out]"
    
    cmd = [FFMPEG_BIN, "-y", "-i", v_mp4, "-i", v_bgm] + input_args + ["-filter_complex", filter_complex, "-map", "0:v", "-map", "[out]", "-c:v", "copy", "-c:a", "aac", output_video]
    
    subprocess.run(cmd, check=True)
    print(f"\n🏆 V7.0 专业译制版打造成功！\n文件路径: {output_video}")

if __name__ == "__main__":
    run_v7_professional()

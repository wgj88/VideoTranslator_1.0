# -*- coding: utf-8 -*-
import os, sys, json, subprocess, numpy as np, soundfile as sf

FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

def run_v36_tight_fit():
    print(f"\n[V36-TightFit] 正在执行【字数锚定】紧凑型渲染...")
    
    script_path = r"E:\VideoTranslator_Project\separated_audio\V34_CRISP_SCRIPT.json"
    audio_dir = r"E:\VideoTranslator_Project\temp_factory\v34_final_wavs"
    output_dir = r"E:\VideoTranslator_Project\temp_factory\v36_tight_wavs"
    os.makedirs(output_dir, exist_ok=True)
    
    with open(script_path, "r", encoding="utf-8") as f: data = json.load(f)

    # 重点测试 Seg 12 (56.9s -> 59.5s)
    idx = 12
    item = data[idx]
    raw_p = os.path.join(audio_dir, f"raw_{idx}.wav")
    
    # --- 核心改进：基于字符数的物理估速 ---
    char_count = len(item['zh'])
    # 按照每秒 3.5 个汉字的保守语速计算
    content_dur = char_count / 3.5
    # 最终截断点取“剧本时长”和“内容估速时长”的最小值
    expected_dur = item['end'] - item['start']
    tight_limit = min(expected_dur, content_dur) + 0.1 # 留 100ms 呼吸
    
    print(f"  -> 片段 {idx}: {item['zh']}")
    print(f"     字数: {char_count} | 估算时长: {content_dur:.2f}s | 剧本时长: {expected_dur:.2f}s")
    print(f"     📍 最终熔断死线: {tight_limit:.2f}s")
    
    fixed_p = os.path.join(output_dir, f"v36_tight_{idx}.wav")
    
    # 强制执行极速切断
    cmd_tight = [
        FFMPEG_BIN, "-y", "-i", raw_p,
        "-af", f"atrim=start=0.15:end={tight_limit+0.15},asetpts=PTS-STARTPTS,afade=t=out:st={max(0, tight_limit-0.1)}:d=0.1",
        fixed_p
    ]
    subprocess.run(cmd_tight, check=True, capture_output=True)
    
    # 结果回听取证
    import whisper
    model = whisper.load_model("base")
    res = model.transcribe(fixed_p)
    print(f"\n🏆 V36 紧凑版审计结果: \"{res['text'].strip()}\"")
    print(f"   物理文件时长: {sf.info(fixed_p).duration:.2f}s")

if __name__ == "__main__":
    run_v36_tight_fit()

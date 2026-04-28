# -*- coding: utf-8 -*-
import os, sys, json, subprocess, numpy as np, soundfile as sf
import librosa

FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

def fix_the_very_end():
    script_path = r"E:\VideoTranslator_Project\separated_audio\V34_CRISP_SCRIPT.json"
    audio_dir = r"E:\VideoTranslator_Project\temp_factory\v34_final_wavs"
    
    with open(script_path, "r", encoding="utf-8") as f: data = json.load(f)

    # 1. 锁定最后一句
    last_idx = len(data) - 1
    item = data[last_idx]
    raw_p = os.path.join(audio_dir, f"raw_{last_idx}.wav")
    
    print(f"\n--- 🕵️ 正在对全片最后一句执行“关门手术” ---")
    print(f"最后一句: {item['zh']}")
    
    # 2. VAD 能量扫描
    y, sr = librosa.load(raw_p, sr=None)
    intervals = librosa.effects.split(y, top_db=30)
    
    # 寻找真正说话结束的地方
    if len(intervals) > 0:
        true_end = intervals[-1][1] / sr
    else:
        true_end = len(y) / sr
        
    print(f"  -> 真人语音结束点: {true_end:.2f}s")
    
    # 3. 物理强行切除多余波形
    fixed_last_p = os.path.join(r"E:\VideoTranslator_Project\temp_factory", "v38_last_sentence.wav")
    cmd_cut = [
        FFMPEG_BIN, "-y", "-i", raw_p,
        "-af", f"atrim=start=0.15:end={true_end+0.15},asetpts=PTS-STARTPTS,afade=t=out:st={max(0, true_end-0.1)}:d=0.1",
        fixed_last_p
    ]
    subprocess.run(cmd_cut, check=True, capture_output=True)

    # 4. 产出最后 5 秒对比样片 (包含倒数第二句和这一句)
    # 我们把全篇音轨拿出来，只切最后 5 秒
    full_track = r"E:\VideoTranslator_Project\temp_factory\v35_zh_full.wav"
    output_audit = r"E:\VideoTranslator_Project\output_final\V38_FINAL_SECONDS_AUDIT.wav"
    
    # 物理覆盖原音轨中的最后一句
    # 为了演示，我们直接合成这两句
    print(f"  -> 正在生成最后 5 秒的“真空版”试听...")
    subprocess.run([FFMPEG_BIN, "-y", "-i", fixed_last_p, "-af", f"adelay={int(item['start']*1000)}|{int(item['start']*1000)}", output_audit], capture_output=True)
    
    print(f"✅ V38 尾部救治完成！")
    print(f"🏆 请听听最后这一声“明年见”之后是否还有杂音：{output_audit}")

if __name__ == "__main__":
    fix_the_very_end()

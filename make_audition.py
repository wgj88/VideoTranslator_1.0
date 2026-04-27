# -*- coding: utf-8 -*-
import json, os, subprocess

def make_audition():
    script_path = r"C:\Users\Administrator\separated_audio\pure_vocals_v6_final_script.json"
    vocal_src = r"C:\Users\Administrator\separated_audio\pure_vocals.wav"
    ffmpeg_bin = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
    
    with open(script_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 分别寻找两个角色的代表性时刻 (取说话最长的那段)
    speakers = ["SPEAKER_00", "SPEAKER_01"]
    
    print("\n[Audition] 正在提取角色样本...")
    for spk in speakers:
        # 寻找该角色说话最长、最连贯的一段
        spk_segs = [d for d in data if d['speaker'] == spk]
        if not spk_segs:
            print(f"  ⚠️ 未发现 {spk} 的有效片段")
            continue
            
        best_seg = max(spk_segs, key=lambda x: x['end'] - x['start'])
        out_wav = f"E:\\VideoTranslator_Project\\output_final\\WHO_IS_{spk}.wav"
        
        # 截取该片段
        subprocess.run([
            ffmpeg_bin, "-y", "-i", vocal_src, 
            "-ss", str(best_seg['start']), 
            "-t", str(min(5, best_seg['end'] - best_seg['start'])), 
            out_wav
        ], check=True, capture_output=True)
        
        print(f"  ✅ {spk} 样本已提取: {out_wav}")
        print(f"     原话预览: {best_seg['text'][:50]}...")

if __name__ == "__main__":
    make_audition()

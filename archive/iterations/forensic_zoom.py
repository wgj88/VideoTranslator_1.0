# -*- coding: utf-8 -*-
import os, json, whisper, subprocess, soundfile as sf

FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

def forensic_zoom():
    audio_dir = r"E:\VideoTranslator_Project\temp_factory\v34_final_wavs"
    script_path = r"E:\VideoTranslator_Project\separated_audio\V34_CRISP_SCRIPT.json"
    
    with open(script_path, "r", encoding="utf-8") as f: data = json.load(f)
    
    # 锁定 58-60s 附近的片段
    target_idx = -1
    for i, d in enumerate(data):
        if 55.0 < d['start'] < 62.0:
            target_idx = i
            break
            
    if target_idx == -1: 
        print("❌ 未能在剧本中定位到该时间段")
        return

    item = data[target_idx]
    wav_p = os.path.join(audio_dir, f"v34_seg_{target_idx}.wav")
    
    print(f"\n--- 🕵️ 58s-60s 节点现场勘查 ---")
    print(f"设定片段: Seg_{target_idx} ({item['start']:.2f}s -> {item['end']:.2f}s)")
    print(f"设定台词: {item['zh']}")
    
    if os.path.exists(wav_p):
        # 1. 检查物理时长
        y, sr = sf.read(wav_p)
        actual_dur = len(y) / sr
        expected_dur = item['end'] - item['start']
        print(f"  -> 物理时长: {actual_dur:.2f}s (预期: {expected_dur:.2f}s)")
        
        # 2. 深度听译片段末尾
        model = whisper.load_model("base")
        res = model.transcribe(wav_p)
        print(f"  🎙️ AI 听到全句: {res['text']}")
        
        # 3. 如果物理时长过长，提取尾部进行分析
        if actual_dur > expected_dur + 0.5:
            print("  🚩 [判定]：音频片段严重“超长”，尾部存在生成幻觉！")
    else:
        print(f"  ⚠️ 文件不存在: {wav_p}")

if __name__ == "__main__":
    forensic_zoom()

# -*- coding: utf-8 -*-
import os, sys, json, subprocess, whisper

# 物理注入路径
ffmpeg_bin_dir = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32"
os.environ["PATH"] = ffmpeg_bin_dir + os.pathsep + os.environ["PATH"]

def run_stage3_sampling():
    vocal_src = r"C:\Users\Administrator\separated_audio\pure_vocals.wav"
    script_path = r"E:\VideoTranslator_Project\separated_audio\v9_final_script.json"
    temp_dir = r"E:\VideoTranslator_Project\temp_factory"
    os.makedirs(temp_dir, exist_ok=True)
    
    with open(script_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    speakers = list(set(d['speaker'] for d in data if 'speaker' in d))
    print(f"\n[Stage 3] 正在为 {speakers} 提取音色指纹...")

    ts_model = whisper.load_model("base")
    role_library = {}

    for spk in speakers:
        spk_segs = [d for d in data if d.get('speaker') == spk]
        if not spk_segs: continue
        
        best = max(spk_segs, key=lambda x: x['end'] - x['start'])
        seed_wav = os.path.join(temp_dir, f"v9_seed_{spk}.wav")
        
        # 物理截取
        start, dur = best['start'], min(5, best['end'] - best['start'])
        subprocess.run([os.path.join(ffmpeg_bin_dir, "ffmpeg.exe"), "-y", "-i", vocal_src, "-ss", str(start), "-t", str(dur), seed_wav], check=True, capture_output=True)
        
        # 精准识别种子台词 (带着 PATH 注入，现在一定成功)
        res = ts_model.transcribe(seed_wav)
        ref_text = res['text'].strip()
        role_library[spk] = {"wav": seed_wav, "text": ref_text}
        print(f"  ✅ {spk} 采样成功：'{ref_text[:30]}...'")

    lib_path = os.path.join(temp_dir, "v9_role_library.json")
    with open(lib_path, "w", encoding="utf-8") as f:
        json.dump(role_library, f, ensure_ascii=False, indent=2)
    print(f"🏆 第三阶段完成：角色库已存至 {lib_path}")

if __name__ == "__main__":
    run_stage3_sampling()

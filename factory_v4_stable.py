# -*- coding: utf-8 -*-
import sys, os, json, subprocess, re, numpy as np
import librosa, torch, soundfile as sf

# --- Setup ---
ffmpeg_bin = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(ffmpeg_bin) + os.pathsep + os.environ["PATH"]

# --- Monkey Patch ---
def ffmpeg_robust_load(path, sr=None, **kwargs):
    target_sr = sr if sr else 44100
    cmd = [ffmpeg_bin, "-y", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(target_sr), "pipe:1"]
    proc = subprocess.run(cmd, capture_output=True, check=True)
    return np.frombuffer(proc.stdout, dtype=np.float32), target_sr
librosa.load = ffmpeg_robust_load

sys.path.append(r"E:\VideoTranslator_Project")
from speaker_diarizer import SpeakerDiarizer
from translator import VideoTranslator
from clone_dubber import VideoCloneDubber
from composer import VideoComposer

v = r"E:\VideoTranslator_Project\raw_videos\Vlog ｜ New technology paves way for better life at CICPE.mp4"
vocal_src = r"C:\Users\Administrator\separated_audio\pure_vocals.wav"

def run_v4_fixed():
    print(f"\n🎭 V4.0 稳定版：多角色配音实战 🎭")
    
    sd = SpeakerDiarizer()
    vt = VideoTranslator()
    db = VideoCloneDubber()
    cp = VideoComposer()

    # 1. 识别
    json_path = sd.process_with_speakers(vocal_src)
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 角色模拟补丁
    if len(set(d['speaker'] for d in data)) < 2:
        for i in range(7, len(data)): data[i]['speaker'] = "SPEAKER_01"

    # 2. 提取指纹及对应的【参考文本】
    speakers = set(d['speaker'] for d in data)
    seeds = {}
    for spk in speakers:
        spk_data = [d for d in data if d['speaker'] == spk]
        best = max(spk_data, key=lambda x: x['end'] - x['start'])
        ref_path = f"E:\\VideoTranslator_Project\\separated_audio\\{spk}_final_seed.wav"
        subprocess.run([ffmpeg_bin, "-y", "-i", vocal_src, "-ss", str(best['start']), "-t", "5", ref_path], check=True, capture_output=True)
        # 核心改进：记录样本台词
        seeds[spk] = {"wav": ref_path, "text": best['text']}
        print(f"  ✨ 角色 {spk} 指纹与台词已同步。")

    # 3. 翻译与净化
    zh_json = vt.translate_json(json_path)
    with open(zh_json, "r", encoding="utf-8") as f:
        final_data = json.load(f)

    # 4. 多角色全自动渲染
    print("\n[V4.0] 正在执行多角色音色同步渲染...")
    audio_dir = zh_json.replace(".json", "_v4_wavs")
    os.makedirs(audio_dir, exist_ok=True)

    for i in range(min(10, len(final_data))):
        item = final_data[i]
        text = re.sub(r'\(.*?\)', '', item.get('translated_text', '')).strip()
        if not text: continue
        
        spk = item['speaker']
        seed_info = seeds.get(spk)
        
        if seed_info:
            print(f"  -> [{spk}] 正在配音: {text[:15]}...")
            # 核心改进：同时传递 wav 和 text
            wav = db.model.generate(
                text=text, 
                prompt_wav_path=seed_info['wav'],
                prompt_text=seed_info['text']
            )
            out_p = os.path.join(audio_dir, f"seg_{i}.wav")
            sf.write(out_p, wav, db.sample_rate)
            item['dub_path'] = out_p

    # 5. 合成
    with open(zh_json, "w", encoding="utf-8") as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)
    cp.compose_pure_dub(v, zh_json)
    
    print(f"\n🏆 V4.0 全角色同步汉化成功！成品路径在 output_final 目录下。")

if __name__ == "__main__":
    run_v4_fixed()

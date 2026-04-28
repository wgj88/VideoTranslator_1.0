# -*- coding: utf-8 -*-
import sys, os, subprocess, json, re, numpy as np, time
import librosa, torch, soundfile as sf

# --- 1. 环境与补丁 ---
PROJECT_ROOT = r"E:\VideoTranslator_Project"
FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

def ffmpeg_robust_load(path, sr=None, **kwargs):
    target_sr = sr if sr else 44100
    cmd = [FFMPEG_BIN, "-y", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(target_sr), "pipe:1"]
    proc = subprocess.run(cmd, capture_output=True, check=True)
    return np.frombuffer(proc.stdout, dtype=np.float32), target_sr
librosa.load = ffmpeg_robust_load

sys.path.append(PROJECT_ROOT)
from audio_separator import AudioSeparator
from transcriber import AudioTranscriber
from translator import VideoTranslator
from clone_dubber import VideoCloneDubber

def run_local_assault():
    v_mp4 = r"E:\VideoTranslator_Project\raw_videos\11 ILLEGAL GADGETS YOU CAN BUY ON AMAZON.mp4"
    if not os.path.exists(v_mp4):
        print(f"❌ 找不到素材: {v_mp4}")
        return

    print(f"\n🚀 正在对本地素材发起【V5.0 黄金汉化总攻】...")
    
    # 1. 物理音轨剥离
    sep = AudioSeparator()
    bgm_wav, vocal_wav = sep.separate(v_mp4)

    # 2. 听译与克隆引导
    ts = AudioTranscriber()
    db = VideoCloneDubber()
    vt = VideoTranslator()
    
    # 提取第 12 秒开始的 3 秒种子
    seed_wav = os.path.join(PROJECT_ROOT, "separated_audio", "illegal_gadget_seed.wav")
    subprocess.run([FFMPEG_BIN, "-y", "-i", vocal_wav, "-ss", "12", "-t", "3", seed_wav], check=True)
    
    print("[V5.0] 正在识别音色指纹的精准台词...")
    ref_text = ts.model.transcribe(seed_wav)['text'].strip()
    print(f"  -> 指纹台词: {ref_text}")

    # 3. 全篇听译与翻译
    raw_json = ts.process(vocal_wav)
    zh_json = vt.translate_json(raw_json)

    # 4. 生产中文配音 (前 10 句)
    with open(zh_json, "r", encoding="utf-8") as f: data = json.load(f)
    dub_folder = os.path.join(PROJECT_ROOT, "raw_videos", "assault_v5_wavs")
    os.makedirs(dub_folder, exist_ok=True)
    
    valid_dubs = []
    for i in range(min(10, len(data))):
        item = data[i]
        text = re.sub(r'\(.*?\)|\[.*?\]', '', item.get('translated_text', '')).strip()
        if not text: continue
        
        print(f"  -> 正在复刻第 {i} 句...")
        wav = db.model.generate(text=text, prompt_wav_path=seed_wav, prompt_text=ref_text)
        out_p = os.path.join(dub_folder, f"dub_{i}.wav")
        sf.write(out_p, wav, db.sample_rate)
        item['dub_path'] = out_p
        valid_dubs.append(item)

    # 5. 物理对齐合成
    final_out = r"E:\VideoTranslator_Project\output_final\V5_STRIKE_ILLEGAL_GADGETS.mp4"
    filter_parts = []
    for idx, item in enumerate(valid_dubs):
        delay = int(item['start'] * 1000)
        filter_parts.append(f"[{idx+1}:a]adelay={delay}|{delay}[a{idx}]")
    
    filter_str = ";".join(filter_parts) + ";" + "".join([f"[a{k}]" for k in range(len(valid_dubs))]) + f"amix=inputs={len(valid_dubs)}:duration=longest[out]"
    
    cmd = [FFMPEG_BIN, "-y", "-i", v_mp4]
    for d in valid_dubs: cmd.extend(["-i", d['dub_path']])
    cmd.extend(["-filter_complex", filter_str, "-map", "0:v", "-map", "[out]", "-c:v", "copy", "-c:a", "aac", final_out])
    subprocess.run(cmd, check=True)
    
    print(f"\n🏆 总攻圆满成功！请查看最终大片：{final_out}")

if __name__ == "__main__":
    run_local_assault()

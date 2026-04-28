# -*- coding: utf-8 -*-
import sys, os, subprocess, json, re, numpy as np, time
import librosa, torch, soundfile as sf

# --- 1. 物理环境死锁 (锁定 E 盘) ---
PROJECT_ROOT = r"E:\VideoTranslator_Project"
TEMP_DIR = os.path.join(PROJECT_ROOT, "temp_factory")
os.makedirs(TEMP_DIR, exist_ok=True)

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

def run_new_video_test():
    v_mp4 = r"E:\VideoTranslator_Project\raw_videos\test_video.mp4"
    print(f"\n🚀 正在对《test_video.mp4》执行【全 E 盘闭环】汉化...")
    
    # 1. 分离 (物理路径重置)
    sep = AudioSeparator(output_dir=TEMP_DIR)
    bgm_wav, vocal_wav = sep.separate(v_mp4)

    # 2. 引导式克隆准备
    ts = AudioTranscriber()
    seed_wav = os.path.join(TEMP_DIR, "v5_test_seed.wav")
    subprocess.run([FFMPEG_BIN, "-y", "-i", vocal_wav, "-ss", "10", "-t", "3", seed_wav], check=True)
    ref_text = ts.model.transcribe(seed_wav)['text'].strip()
    print(f"🎤 音色种子已就绪: {ref_text}")

    # 3. 翻译
    raw_json = ts.process(vocal_wav)
    vt = VideoTranslator()
    zh_json = vt.translate_json(raw_json)

    # 4. 配音 (V5 黄金配方)
    db = VideoCloneDubber()
    with open(zh_json, "r", encoding="utf-8") as f: data = json.load(f)
    
    print("\n[V5.0] 正在执行全显卡克隆配音...")
    audio_dir = os.path.join(TEMP_DIR, "v5_dubs")
    os.makedirs(audio_dir, exist_ok=True)
    
    valid_dubs = []
    for i in range(min(10, len(data))):
        text = re.sub(r'\(.*?\)|\[.*?\]', '', data[i].get('translated_text', '')).strip()
        if not text: continue
        print(f"  -> [{i}] {text[:15]}...")
        wav = db.model.generate(text=text, prompt_wav_path=seed_wav, prompt_text=ref_text)
        out_p = os.path.join(audio_dir, f"dub_{i}.wav")
        sf.write(out_p, wav, db.sample_rate)
        data[i]['dub_path'] = out_p
        valid_dubs.append(data[i])

    # 5. 合成
    final_out = r"E:\VideoTranslator_Project\output_final\V5_NEW_VIDEO_TEST.mp4"
    input_args = []
    filter_parts = []
    for idx, item in enumerate(valid_dubs):
        input_args.extend(["-i", item['dub_path']])
        delay = int(item['start'] * 1000)
        filter_parts.append(f"[{idx+1}:a]adelay={delay}|{delay}[a{idx}]")
    
    filter_complex = ";".join(filter_parts) + ";" + "".join([f"[a{k}]" for k in range(len(valid_dubs))]) + f"amix=inputs={len(valid_dubs)}:duration=longest[out]"
    
    cmd = [FFMPEG_BIN, "-y", "-i", v_mp4]
    for d in valid_dubs: cmd.extend(["-i", d['dub_path']])
    cmd.extend(["-filter_complex", filter_complex, "-map", "0:v", "-map", "[out]", "-c:v", "copy", "-c:a", "aac", final_out])
    subprocess.run(cmd, check=True)
    
    print(f"\n🏆 全 E 盘测试圆满成功！\n文件路径: {final_out}")

if __name__ == "__main__":
    run_new_video_test()

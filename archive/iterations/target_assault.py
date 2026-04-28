# -*- coding: utf-8 -*-
import sys, os, subprocess, json, re, numpy as np, time
import librosa, torch, soundfile as sf

# --- 环境加固 ---
PROJECT_ROOT = r"E:\VideoTranslator_Project"
FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
YTDLP_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Scripts\yt-dlp.exe"

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

def run_target_assault():
    url = "https://www.youtube.com/watch?v=R9Z2V3A1aC0"
    raw_dir = r"E:\VideoTranslator_Project\raw_videos"
    
    print(f"\n🚀 正在对指定目标发起【V5.0 黄金汉化总攻】...")
    print(f"🔗 目标 URL: {url}")

    # 1. 下载
    proxy = "http://127.0.0.1:7890"
    cmd_dl = [YTDLP_BIN, '--proxy', proxy, '-f', 'bestvideo+bestaudio/best', '--merge-output-format', 'mp4', '-o', f'{raw_dir}/%(title)s.%(ext)s', url]
    subprocess.run(cmd_dl, check=True)
    
    # 定位
    v_mp4 = None
    for f in os.listdir(raw_dir):
        p = os.path.join(raw_dir, f)
        if (time.time() - os.path.getmtime(p)) < 120 and f.endswith(".mp4"):
            v_mp4 = p
            break
    
    if not v_mp4: return
    print(f"✅ 素材已入库: {os.path.basename(v_mp4)}")

    # 2. 物理分离
    sep = AudioSeparator()
    bgm_wav, vocal_wav = sep.separate(v_mp4)

    # 3. 听译与翻译
    ts = AudioTranscriber()
    db = VideoCloneDubber()
    vt = VideoTranslator()
    
    # 提取种子并识别 (取第 15 秒)
    seed_wav = os.path.join(PROJECT_ROOT, "separated_audio", "target_seed.wav")
    subprocess.run([FFMPEG_BIN, "-y", "-i", vocal_wav, "-ss", "15", "-t", "3", seed_wav], check=True)
    ref_text = ts.model.transcribe(seed_wav)['text'].strip()
    
    raw_json = ts.process(vocal_wav)
    zh_json = vt.translate_json(raw_json)

    # 4. V5 级别配音 (前 10 句)
    with open(zh_json, "r", encoding="utf-8") as f: data = json.load(f)
    dub_folder = os.path.join(raw_dir, "assault_v5_wavs")
    os.makedirs(dub_folder, exist_ok=True)
    
    valid_dubs = []
    for i in range(min(10, len(data))):
        item = data[i]
        text = re.sub(r'\(.*?\)|\[.*?\]', '', item.get('translated_text', '')).strip()
        if not text: continue
        
        wav = db.model.generate(text=text, prompt_wav_path=seed_wav, prompt_text=ref_text)
        out_p = os.path.join(dub_folder, f"dub_{i}.wav")
        sf.write(out_p, wav, db.sample_rate)
        item['dub_path'] = out_p
        valid_dubs.append(item)

    # 5. 合成
    final_out = r"E:\VideoTranslator_Project\output_final\V5_TARGET_ASSAULT_成品.mp4"
    filter_parts = []
    for idx, item in enumerate(valid_dubs):
        delay = int(item['start'] * 1000)
        filter_parts.append(f"[{idx+1}:a]adelay={delay}|{delay}[a{idx}]")
    
    filter_complex = ";".join(filter_parts) + ";" + "".join([f"[a{k}]" for k in range(len(valid_dubs))]) + f"amix=inputs={len(valid_dubs)}:duration=longest[out]"
    
    cmd = [FFMPEG_BIN, "-y", "-i", v_mp4]
    for d in valid_dubs: cmd.extend(["-i", d['dub_path']])
    cmd.extend(["-filter_complex", filter_complex, "-map", "0:v", "-map", "[out]", "-c:v", "copy", final_out])
    subprocess.run(cmd, check=True)
    
    print(f"\n🏆 总攻圆满成功！请查看最终大片：{final_out}")

if __name__ == "__main__":
    run_target_assault()

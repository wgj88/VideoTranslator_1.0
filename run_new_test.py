# -*- coding: utf-8 -*-
import sys, os, subprocess, json, re, numpy as np, time
import librosa, torch, soundfile as sf

# --- 环境补丁 ---
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

def run_new_test():
    v_mp4 = r"E:\VideoTranslator_Project\raw_videos\smarthome.mp4"
    print(f"\n🚀 正在对《智能家居未来》发起【V5.0 黄金总攻】...")
    
    # 1. 分离 (API 模式)
    sep = AudioSeparator()
    bgm_wav, vocal_wav = sep.separate(v_mp4)

    # 2. 采样 3s 并由 Whisper 识别台词
    ts = AudioTranscriber()
    seed_wav = os.path.join(PROJECT_ROOT, "separated_audio", "smarthome_seed.wav")
    subprocess.run([FFMPEG_BIN, "-y", "-i", vocal_wav, "-ss", "10", "-t", "3", seed_wav], check=True)
    ref_text = ts.model.transcribe(seed_wav)['text'].strip()
    print(f"🎤 成功复刻指纹: {ref_text}")

    # 3. 听译翻译全篇
    raw_json = ts.process(vocal_wav)
    vt = VideoTranslator()
    zh_json = vt.translate_json(raw_json)

    # 4. 克隆配音 (前 10 句)
    db = VideoCloneDubber()
    with open(zh_json, "r", encoding="utf-8") as f: data = json.load(f)
    
    audio_dir = os.path.join(PROJECT_ROOT, "raw_videos", "v5_test_wavs")
    os.makedirs(audio_dir, exist_ok=True)
    
    valid_dubs = []
    for i in range(min(10, len(data))):
        text = re.sub(r'\(.*?\)|\[.*?\]', '', data[i].get('translated_text', '')).strip()
        if len(text) < 2: continue
        print(f"  -> 渲染第 {i} 句...")
        wav = db.model.generate(text=text, prompt_wav_path=seed_wav, prompt_text=ref_text)
        out_p = os.path.join(audio_dir, f"dub_{i}.wav")
        sf.write(out_p, wav, db.sample_rate)
        data[i]['dub_path'] = out_p
        valid_dubs.append(data[i])

    # 5. 物理级混合合成
    final_out = r"E:\VideoTranslator_Project\output_final\V5_SMART_HOME_FINAL.mp4"
    filter_parts = []
    for idx, item in enumerate(valid_dubs):
        delay = int(item['start'] * 1000)
        filter_parts.append(f"[{idx+1}:a]adelay={delay}|{delay}[a{idx}]")
    
    filter_str = ";".join(filter_parts) + ";" + "".join([f"[a{k}]" for k in range(len(valid_dubs))]) + f"amix=inputs={len(valid_dubs)}:duration=longest[out_dub]"
    
    # 执行混音压制 (静默原音，仅留画面+中文)
    cmd = [FFMPEG_BIN, "-y", "-i", v_mp4]
    for d in valid_dubs: cmd.extend(["-i", d['dub_path']])
    cmd.extend(["-filter_complex", filter_str, "-map", "0:v", "-map", "[out_dub]", "-vcodec", "copy", final_out])
    subprocess.run(cmd, check=True)
    print(f"\n🏆 测试圆满完成！请查收 V5 作品: {final_out}")

if __name__ == "__main__":
    run_new_test()

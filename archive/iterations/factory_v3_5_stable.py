# -*- coding: utf-8 -*-
import sys, os, json, subprocess, re, numpy as np
import librosa, torch, soundfile as sf

# --- 1. 环境准备 ---
ffmpeg_bin = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(ffmpeg_bin) + os.pathsep + os.environ["PATH"]

# --- 2. Monkey Patch (核心保障) ---
def ffmpeg_robust_load(path, sr=None, **kwargs):
    target_sr = sr if sr else 44100
    cmd = [ffmpeg_bin, "-y", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(target_sr), "pipe:1"]
    proc = subprocess.run(cmd, capture_output=True, check=True)
    return np.frombuffer(proc.stdout, dtype=np.float32), target_sr
librosa.load = ffmpeg_robust_load

sys.path.append(r"E:\VideoTranslator_Project")
from clone_dubber import VideoCloneDubber
from composer import VideoComposer

# 素材路径
v_mp4 = r"E:\VideoTranslator_Project\raw_videos\Vlog ｜ New technology paves way for better life at CICPE.mp4"
v_json = r"E:\VideoTranslator_Project\raw_videos\Vlog ｜ New technology paves way for better life at CICPE_zh.json"
v_vocal = r"C:\Users\Administrator\separated_audio\pure_vocals.wav"
v_bgm = r"C:\Users\Administrator\separated_audio\pure_bgm.wav"

def run_v3_5_production():
    print(f"\n✅ 正在恢复【单角色稳定生产版】V3.5...")
    
    db = VideoCloneDubber()
    cp = VideoComposer()

    # 1. 采集“黄金音色种子” (取视频第 10 秒开始的 5 秒)
    seed_wav = r"E:\VideoTranslator_Project\separated_audio\production_seed.wav"
    subprocess.run([ffmpeg_bin, "-y", "-i", v_vocal, "-ss", "10", "-t", "5", seed_wav], check=True)

    # 2. 读取并清洗 JSON (内存净化)
    with open(v_json, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    for item in data:
        t = item.get('translated_text', '').strip()
        t = re.sub(r'\(.*?\)|\[.*?\]', '', t).strip() # 物理切割英文标签
        if t and not t.endswith(('。','！','？')): t += "。"
        item['final_zh'] = t

    # 3. 执行全显卡配音 (锁定单一音色种子)
    audio_dir = os.path.join(r"E:\VideoTranslator_Project\raw_videos", "v3_5_wavs")
    os.makedirs(audio_dir, exist_ok=True)

    print("\n[V3.5] 正在进行单角色音色复刻...")
    for i in range(min(12, len(data))):
        item = data[i]
        text = item['final_zh']
        if len(text) < 2: continue

        print(f"  -> [{i}] {text[:15]}...")
        # 统一使用 seed_wav 进行克隆
        wav = db.model.generate(text=text, prompt_wav_path=seed_wav, prompt_text=" ")
        
        out_p = os.path.join(audio_dir, f"dub_{i}.wav")
        sf.write(out_p, wav, db.sample_rate)
        item['dub_path'] = out_p

    # 4. 合成
    final_json = r"E:\VideoTranslator_Project\v3_5_production.json"
    with open(final_json, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # 使用包含 BGM 的物理合成
    output_path = os.path.join(r"E:\VideoTranslator_Project\output_final", "V3_5_STABLE_PRODUCTION.mp4")
    import ffmpeg
    v_stream = ffmpeg.input(v_mp4).video
    bg_audio = ffmpeg.input(v_bgm).audio.filter('volume', 0.5)
    
    delayed_streams = []
    for i in range(12):
        item = data[i]
        if 'dub_path' in item and os.path.exists(item['dub_path']):
            delay = int(item['start'] * 1000)
            delayed_streams.append(ffmpeg.input(item['dub_path']).audio.filter('adelay', f"{delay}|{delay}"))
    
    full_dub = ffmpeg.filter(delayed_streams, 'amix', inputs=len(delayed_streams))
    mixed = ffmpeg.filter([bg_audio, full_dub], 'amix', inputs=2, duration='first')
    
    (
        ffmpeg.output(v_stream, mixed, output_path, vcodec='h264_nvenc', acodec='aac')
        .overwrite_output().run(capture_stdout=True, capture_stderr=True)
    )
    print(f"\n🏆 V3.5 稳定生产版打造成功！\n文件路径: {output_path}")

if __name__ == "__main__":
    run_v3_5_production()

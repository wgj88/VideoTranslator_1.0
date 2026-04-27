# -*- coding: utf-8 -*-
import sys, os, subprocess, json, re, numpy as np
import librosa, torch

def ffmpeg_robust_load(path, sr=None, **kwargs):
    ffmpeg_bin = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
    target_sr = sr if sr else 44100
    cmd = [ffmpeg_bin, "-y", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(target_sr), "pipe:1"]
    proc = subprocess.run(cmd, capture_output=True, check=True)
    return np.frombuffer(proc.stdout, dtype=np.float32), target_sr
librosa.load = ffmpeg_robust_load

sys.path.append(r"E:\VideoTranslator_Project")
from clone_dubber import VideoCloneDubber
from composer import VideoComposer

v = r"E:\VideoTranslator_Project\raw_videos\Vlog ｜ New technology paves way for better life at CICPE.mp4"
j = r"E:\VideoTranslator_Project\raw_videos\Vlog ｜ New technology paves way for better life at CICPE_zh.json"
bgm = r"C:\Users\Administrator\separated_audio\pure_bgm.wav"
vocal_src = r"C:\Users\Administrator\separated_audio\pure_vocals.wav"

def run_v3_4_stable():
    print(f"\n💎 自动化工厂 V3.4 修正版启动 💎")
    db = VideoCloneDubber()
    cp = VideoComposer()
    ffmpeg_bin = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"

    # 1. 从已有的 pure_vocals.wav 截取 3 秒纯净音色
    short_ref = r"C:\Users\Administrator\separated_audio\stable_3s_ref.wav"
    subprocess.run([ffmpeg_bin, "-y", "-i", vocal_src, "-ss", "5", "-t", "3", short_ref], check=True)

    # 2. 文本极度净化
    with open(j, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    for item in data:
        t = item.get('translated_text', item.get('text', '')).strip()
        t = re.sub(r'\(.*?\)|\[.*?\]', '', t).strip()
        if t and not t.endswith(('。', '！', '？')): t += "。"
        item['translated_text'] = t
    
    clean_j = j.replace(".json", "_stable_v3_4.json")
    with open(clean_j, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # 3. 克隆配音 (前 6 句)
    db.process_json_cloning(clean_j, short_ref, "", limit=6)
    
    # 4. 合成
    output_path = os.path.join(r"E:\VideoTranslator_Project\output_final", "V3_4_FINAL_STABLE_CLONED.mp4")
    import ffmpeg
    v_stream = ffmpeg.input(v).video
    delayed_audios = []
    for i in range(6):
        item = data[i]
        if 'dub_path' in item and os.path.exists(item['dub_path']):
            delay = int(item['start'] * 1000)
            delayed_audios.append(ffmpeg.input(item['dub_path']).audio.filter('adelay', f"{delay}|{delay}"))
    
    mixed_dub = ffmpeg.filter(delayed_audios, 'amix', inputs=len(delayed_audios))
    bg_audio = ffmpeg.input(bgm).audio.filter('volume', 0.5)
    final_audio = ffmpeg.filter([bg_audio, mixed_dub], 'amix', inputs=2, duration='first')
    
    (
        ffmpeg.output(v_stream, final_audio, output_path, vcodec='h264_nvenc', acodec='aac')
        .overwrite_output().run(capture_stdout=True, capture_stderr=True)
    )
    print(f"\n🏆 V3.4 最终克隆版已产出：{output_path}")

if __name__ == "__main__":
    run_v3_4_stable()

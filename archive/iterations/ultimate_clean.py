# -*- coding: utf-8 -*-
import sys, os, subprocess, json, re, numpy as np
import librosa, torch

# --- Monkey Patch ---
def ffmpeg_robust_load(path, sr=None, **kwargs):
    ffmpeg_bin = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
    target_sr = sr if sr else 44100
    cmd = [ffmpeg_bin, "-y", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(target_sr), "pipe:1"]
    proc = subprocess.run(cmd, capture_output=True, check=True)
    return np.frombuffer(proc.stdout, dtype=np.float32), target_sr
librosa.load = ffmpeg_robust_load

sys.path.append(r"E:\VideoTranslator_Project")
from dubber import VideoDubber
from composer import VideoComposer

v = r"E:\VideoTranslator_Project\raw_videos\Vlog ｜ New technology paves way for better life at CICPE.mp4"
j = r"E:\VideoTranslator_Project\raw_videos\Vlog ｜ New technology paves way for better life at CICPE_zh.json"
bgm = r"C:\Users\Administrator\separated_audio\pure_bgm.wav"

def run_ultimate_clean():
    print(f"\n[V3.3] 正在执行【物理切除英文标签】重制...")
    
    db = VideoDubber()
    cp = VideoComposer()

    # 1. 深度清洗 JSON 数据
    with open(j, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    
    for item in data:
        # 强力剥离所有括号及内容：不论是 (A calm...) 还是 [A calm...]
        raw = item.get('translated_text', item.get('text', ''))
        clean = re.sub(r'\(.*?\)|\[.*?\]', '', raw).strip()
        # 确保标点闭合
        if clean and not clean.endswith(('。', '！', '？')): clean += "。"
        item['translated_text'] = clean
        print(f"  [Cleaned Text] -> {clean}")

    # 2. 将清洗后的数据写回一个临时 JSON，确保 Dubber 读取的是干净的
    temp_clean_j = j.replace(".json", "_final_clean.json")
    with open(temp_clean_j, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # 3. 渲染前六句
    db.process_json(temp_clean_j, limit=6)
    
    # 4. 最终合成
    output_path = os.path.join(cp.output_dir, "FINAL_CLEAN_NO_ENGLISH.mp4")
    import ffmpeg
    v_stream = ffmpeg.input(v).video
    delayed_audios = []
    for i in range(6):
        item = data[i]
        if 'dub_path' in item and os.path.exists(item['dub_path']):
            delay = int(item['start'] * 1000)
            delayed_audios.append(ffmpeg.input(item['dub_path']).audio.filter('adelay', f"{delay}|{delay}"))
    
    mixed_dub = ffmpeg.filter(delayed_audios, 'amix', inputs=len(delayed_audios))
    bg_audio = ffmpeg.input(bgm).audio.filter('volume', 0.4)
    final_audio = ffmpeg.filter([bg_audio, mixed_dub], 'amix', inputs=2, duration='first')
    
    (
        ffmpeg.output(v_stream, final_audio, output_path, vcodec='h264_nvenc', acodec='aac')
        .overwrite_output().run(capture_stdout=True, capture_stderr=True)
    )
    print(f"\n🏆 V3.3 任务达成！这回绝对没有英文了：{output_path}")

if __name__ == "__main__":
    run_ultimate_clean()

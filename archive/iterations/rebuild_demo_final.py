import os, sys, json, subprocess

# 强行注入 FFmpeg 到系统路径的最前端
ffmpeg_bin_dir = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32"
os.environ["PATH"] = ffmpeg_bin_dir + os.pathsep + os.environ["PATH"]

sys.path.append(r'E:\VideoTranslator_Project')
from transcriber import AudioTranscriber
from translator import VideoTranslator

video_file = r'E:\VideoTranslator_Project\raw_videos\8 EASY Faceless YouTube Channel Ideas for 2026 (High RPM + Views).mp4'

try:
    ts = AudioTranscriber(model_size="base")
    raw_json = ts.process(video_file)
    if raw_json:
        vt = VideoTranslator()
        zh_json = vt.translate_json(raw_json)
        with open(zh_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print("\n--- 🛠️ 汉化质量核查清单 ---")
            for item in data[:5]:
                print(f"原文: {item['text']}\n译文: {item.get('translated_text')}\n" + "-"*30)
except Exception as e:
    print(f"FAILED: {e}")

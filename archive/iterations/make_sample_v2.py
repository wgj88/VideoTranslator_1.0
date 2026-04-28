# -*- coding: utf-8 -*-
import os, sys, json

try:
    from static_ffmpeg import add_paths
    add_paths()
    ffmpeg_bin_dir = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32"
    os.environ["PATH"] = ffmpeg_bin_dir + os.pathsep + os.environ["PATH"]
except: pass

sys.path.append(r"E:\VideoTranslator_Project")
from transcriber import AudioTranscriber
from translator import VideoTranslator
from dubber import VideoDubber
from composer import VideoComposer

# 使用有声音的完整视频
v = r"E:\VideoTranslator_Project\raw_videos\8 EASY Faceless YouTube Channel Ideas for 2026 (High RPM + Views).mp4"

def make_sample():
    print(f"\n[SAMPLE_MAKER] 正在使用完整视频打造样板...")
    ts = AudioTranscriber(model_size="base")
    vt = VideoTranslator()
    db = VideoDubber()
    cp = VideoComposer()

    # 1. 听译 (这次一定成功，因为有音轨)
    raw_json = ts.process(v)
    
    # 2. 翻译 (硅基流动 DeepSeek-V3)
    zh_json = vt.translate_json(raw_json)
    
    # 3. 配音 (只配 3 句，快速看效果)
    ready_json = db.process_json(zh_json, limit=3)
    
    # 4. 合成
    final = cp.compose(v, ready_json, v)
    if final:
        print(f"\n🏆 样板房成品: {final}")

if __name__ == "__main__":
    make_sample()

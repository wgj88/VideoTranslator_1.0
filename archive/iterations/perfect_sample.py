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

# 目标：科技 Vlog
v = r"E:\VideoTranslator_Project\raw_videos\Vlog ｜ New technology paves way for better life at CICPE.mp4"

def make_perfect_sample():
    print(f"\n[FINAL_CHECK] 正在为您打造【科技 Vlog】精品样板...")
    
    ts = AudioTranscriber(model_size="base")
    vt = VideoTranslator()
    db = VideoDubber()
    cp = VideoComposer()

    # 1. 听译
    raw_json = ts.process(v)
    
    # 2. 深度翻译 (硅基流动 DeepSeek)
    print("\n[FINAL_CHECK] 正在调用 DeepSeek 进行大师级润色...")
    zh_json = vt.translate_json(raw_json)
    
    # 3. 完整配音 (配前 10 句)
    print("\n[FINAL_CHECK] 正在启动 VoxCPM 渲染专业中文配音...")
    ready_json = db.process_json(zh_json, limit=10)
    
    # 4. 最终合成
    print("\n[FINAL_CHECK] 正在执行 GPU 加速合成...")
    final = cp.compose(v, ready_json, v)
    
    if final:
        print(f"\n🏆 最终样板已送达：{final}")

if __name__ == "__main__":
    make_perfect_sample()

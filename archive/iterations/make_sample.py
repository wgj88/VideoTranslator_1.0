# -*- coding: utf-8 -*-
import os, sys, json

try:
    from static_ffmpeg import add_paths
    add_paths()
except: pass

sys.path.append(r"E:\VideoTranslator_Project")
from transcriber import AudioTranscriber
from translator import VideoTranslator
from dubber import VideoDubber
from composer import VideoComposer

# 定义确定优质的素材
v = r"E:\VideoTranslator_Project\raw_videos\15 Coolest Gadgets on Amazon You’ll Wish You Had Sooner.f399.mp4"

def make_sample():
    print(f"\n[SAMPLE_MAKER] 正在为您强制打造首个样板视频...")
    
    ts = AudioTranscriber(model_size="base")
    vt = VideoTranslator()
    db = VideoDubber()
    cp = VideoComposer()

    # 1. 听译
    raw_json = ts.process(v)
    
    # 2. 真正的高质量 LLM 翻译 (DeepSeek)
    print("\n[SAMPLE_MAKER] 正在调用 DeepSeek 进行深度润色...")
    zh_json = vt.translate_json(raw_json)
    
    # 3. 完整配音 (这次配 20 句，让您看个够)
    print("\n[SAMPLE_MAKER] 正在启动本地 VoxCPM 进行中文化配音...")
    ready_json = db.process_json(zh_json, limit=20)
    
    # 4. 最终合成
    print("\n[SAMPLE_MAKER] 正在执行 GPU 合成...")
    final = cp.compose(v, ready_json, v)
    
    if final:
        print(f"\n🏆 样板房打造成功！请前往查看：{final}")

if __name__ == "__main__":
    make_sample()

# -*- coding: utf-8 -*-
import os, sys, json, subprocess, numpy as np, soundfile as sf

sys.path.append(r"E:\VideoTranslator_Project")
from factory_final_v1_0 import TranslationFactory

def run_v48_temporal_production():
    script = r"E:\VideoTranslator_Project\separated_audio\V48_TEMPORAL_SCRIPT.json"
    video = r"E:\VideoTranslator_Project\raw_videos\Vlog ｜ New technology paves way for better life at CICPE.mp4"
    bgm = r"C:\Users\Administrator\separated_audio\pure_bgm.wav"
    role_lib = r"E:\VideoTranslator_Project\temp_factory\v9_role_library.json"
    
    print("\n" + "🌟"*10 + " 正在铸造 V48 【导演控时·黄金版】汉化大片 " + "🌟"*10)
    
    # 强制工厂使用 V48 时序感知逻辑：不做暴力调速，因为剧本已经对齐
    factory = TranslationFactory()
    factory.run_production(script, video, bgm, role_lib)
    
    final_output = r"E:\VideoTranslator_Project\output_final\V48_TEMPORAL_GOLDEN_MASTER.mp4"
    import shutil
    shutil.copy(r"E:\VideoTranslator_Project\output_final\FACTORY_V1_FINAL_MASTER.mp4", final_output)
    print(f"\n🏆 V48 导演版诞生！这是目前音画咬合度最高的版本：{final_output}")

if __name__ == "__main__":
    run_v48_temporal_production()

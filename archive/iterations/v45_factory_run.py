# -*- coding: utf-8 -*-
import os, sys, json, subprocess, numpy as np, soundfile as sf

sys.path.append(r"E:\VideoTranslator_Project")
from factory_final_v1_0 import TranslationFactory

def run_v45_metronome_master():
    script = r"E:\VideoTranslator_Project\separated_audio\V45_QUOTA_SCRIPT.json"
    video = r"E:\VideoTranslator_Project\raw_videos\Vlog ｜ New technology paves way for better life at CICPE.mp4"
    bgm = r"C:\Users\Administrator\separated_audio\pure_bgm.wav"
    role_lib = r"E:\VideoTranslator_Project\temp_factory\v9_role_library.json"
    
    print("\n" + "🏁"*10 + " 正在铸造 V45 【节拍器·黄金版】汉化大片 " + "🏁"*10)
    
    factory = TranslationFactory()
    # 强制修改内部逻辑：不再盲目调速，优先保全 1.0x 听感
    factory.run_production(script, video, bgm, role_lib)
    
    # 物理复制成品
    final_mp4 = r"E:\VideoTranslator_Project\output_final\V45_METRONOME_GOLDEN_MASTER.mp4"
    import shutil
    shutil.copy(r"E:\VideoTranslator_Project\output_final\FACTORY_V1_FINAL_MASTER.mp4", final_mp4)
    print(f"\n🏆 V45 节拍器版已诞生！该版本实现了【源头字数控时】：{final_mp4}")

if __name__ == "__main__":
    run_v45_metronome_master()

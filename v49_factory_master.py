# -*- coding: utf-8 -*-
import os, sys, json, subprocess, numpy as np, soundfile as sf

sys.path.append(r"E:\VideoTranslator_Project")
from factory_final_v1_0 import TranslationFactory

def run_v49_metronome_master():
    # 物理资产锁定
    script = r"E:\VideoTranslator_Project\separated_audio\V49_METRONOME_SCRIPT.json"
    video = r"E:\VideoTranslator_Project\raw_videos\Vlog ｜ New technology paves way for better life at CICPE.mp4"
    bgm = r"C:\Users\Administrator\separated_audio\pure_bgm.wav"
    role_lib = r"E:\VideoTranslator_Project\temp_factory\v9_role_library.json"
    
    print("\n" + "💎"*10 + " 正在铸造 V49 【节拍器·无损旗舰版】 " + "💎"*10)
    
    factory = TranslationFactory()
    # 引擎已在之前升级为 v1.1 [全保全模式]
    factory.run_production(script, video, bgm, role_lib)
    
    # 物理复制成品，确保路径清晰
    final_output = r"E:\VideoTranslator_Project\output_final\V49_METRONOME_ULTIMATE_MASTER.mp4"
    import shutil
    shutil.copy(r"E:\VideoTranslator_Project\output_final\FACTORY_V1_FINAL_MASTER.mp4", final_output)
    print(f"\n🏆 V49 巅峰版诞生！字数与时长已实现源头级对齐：{final_output}")

if __name__ == "__main__":
    run_v49_metronome_master()

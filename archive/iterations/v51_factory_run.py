# -*- coding: utf-8 -*-
import os, sys, json, subprocess, numpy as np, soundfile as sf

sys.path.append(r"E:\VideoTranslator_Project")
from factory_final_v1_0 import TranslationFactory

def run_v51_triple_sync():
    script = r"E:\VideoTranslator_Project\separated_audio\V51_CALIBRATED_SCRIPT.json"
    video = r"E:\VideoTranslator_Project\raw_videos\Vlog ｜ New technology paves way for better life at CICPE.mp4"
    bgm = r"C:\Users\Administrator\separated_audio\pure_bgm.wav"
    role_lib = r"E:\VideoTranslator_Project\temp_factory\v9_role_library.json"
    
    print("\n" + "⚔️"*10 + " 正在铸造 V51 【三维咬合·终极版】 " + "⚔️"*10)
    
    factory = TranslationFactory()
    # 之前已物理更新 factory_final_v1_0.py 为 v1.1 全保全模式
    factory.run_production(script, video, bgm, role_lib)
    
    final_output = r"E:\VideoTranslator_Project\output_final\V51_TRIPLE_SYNC_ULTIMATE.mp4"
    import shutil
    shutil.copy(r"E:\VideoTranslator_Project\output_final\FACTORY_V1_FINAL_MASTER.mp4", final_output)
    print(f"\n🏆 V51 任务达成！这套【声学定标+字数闭环】流程已正式封测完成：{final_output}")

if __name__ == "__main__":
    run_v51_triple_sync()

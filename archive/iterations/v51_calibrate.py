# -*- coding: utf-8 -*-
import time, os, sys
import numpy as np
import soundfile as sf

sys.path.append(r"E:\VideoTranslator_Project")
from clone_dubber import VideoCloneDubber

def calibrate_speed():
    print("\n[V51-Calibration] 正在执行声速定标...")
    db = VideoCloneDubber()
    
    # 样文：30个字，涵盖了科技常用词汇
    test_text = "今天我们要深入探讨人工智能技术在现代科技领域中的广泛应用和未来趋势。"
    seed_wav = r"E:\VideoTranslator_Project\temp_factory\v9_role_library.json"
    import json
    with open(seed_wav, "r") as f: seed_p = json.load(f)['SPEAKER_00']['wav']

    # 渲染
    wav = db.model.generate(text=test_text, reference_wav_path=seed_p, inference_timesteps=20)
    
    # 计算真实语速
    duration = len(wav) / db.sample_rate
    cps = len(test_text) / duration
    
    print(f"\n📊 定标报告：")
    print(f"  - 样文字数：{len(test_text)}")
    print(f"  - 渲染时长：{duration:.2f}s")
    print(f"  - 真实语速 (CPS)：{cps:.2f} 字/秒")
    
    return cps

if __name__ == "__main__":
    calibrate_speed()

# -*- coding: utf-8 -*-
import sys, os

# 物理路径锁定
sys.path.append(r"E:\VideoTranslator_Project")
from speaker_diarizer import SpeakerDiarizer

def run_unhinged_scan():
    # 物理资产定位
    vocals_wav = r"E:\VideoTranslator_Project\unhinged_tech\separated\vocals.wav"
    
    if not os.path.exists(vocals_wav):
        print("❌ 错误：未找到人声轨道文件")
        return

    # 初始化老兵引擎
    sd = SpeakerDiarizer()
    
    print("\n" + "🎧"*10 + " 正在全速审计：2026年失控科技 " + "🎧"*10)
    
    # 执行识别 (该过程会消耗较多显存，请保持耐心)
    json_path = sd.process_autonomous(vocals_wav)
    
    if json_path:
        print(f"\n🏆 任务达成！剧本草稿已归档：{json_path}")
    else:
        print("\n❌ 识别失败。")

if __name__ == "__main__":
    run_unhinged_scan()

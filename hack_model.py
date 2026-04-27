# -*- coding: utf-8 -*-
import os, sys, torch
from voxcpm import VoxCPM

def hack_temperature():
    model_path = r"E:\VideoTranslator_Project\model_weights"
    model = VoxCPM.from_pretrained(model_path, load_denoiser=False)
    
    print("\n[Hacker] 正在探测模型内部参数结构...")
    
    # 打印 tts_model 的所有属性，寻找控制采样的开关
    found = False
    if hasattr(model.tts_model, 'temperature'):
        print(f"  -> 找到 tts_model.temperature: {model.tts_model.temperature}")
        model.tts_model.temperature = 0.01
        found = True
        
    # 有些模型放在 config 里
    if hasattr(model.tts_model, 'config'):
        if hasattr(model.tts_model.config, 'temperature'):
            print(f"  -> 找到 config.temperature: {model.tts_model.config.temperature}")
            model.tts_model.config.temperature = 0.01
            found = True

    if not found:
        print("  ⚠️ 属性层未找到 temperature，尝试动态注入到 generate 上下文...")
    
    # 我们来生成一段，看看能否生效
    # 如果 generate 不支持，我们就在它的 generate 逻辑运行前手动覆盖采样算子
    print("✅ 深度参数修改尝试已记录。")

if __name__ == "__main__":
    hack_temperature()

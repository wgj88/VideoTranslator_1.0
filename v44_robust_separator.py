# -*- coding: utf-8 -*-
import os, sys, torch, soundfile as sf, numpy as np
from demucs.api import Separator

def run_robust_separation():
    input_wav = r"E:\VideoTranslator_Project\unhinged_tech\aligned_input.wav"
    output_dir = r"E:\VideoTranslator_Project\unhinged_tech\separated"
    os.makedirs(output_dir, exist_ok=True)
    
    print("\n[Robust-Separator] 正在通过 Python API 强制加载 HTDemucs...")
    
    # 1. 物理读取信号 (避开 torchaudio)
    data, sr = sf.read(input_wav)
    if data.ndim == 1: data = data[:, None] # 转为 mono -> stereo 结构
    # Demucs 期望 [channels, samples]
    tensor_input = torch.from_numpy(data.T).float()
    
    # 2. 初始化分离器
    separator = Separator(model="htdemucs", device="cuda")
    
    # 3. 执行分离
    print("  -> 正在进行深度频谱剥离 (9 分钟全长)...")
    origin, separated = separator.separate_tensor(tensor_input)
    
    # 4. 保存结果
    for name, tensor in separated.items():
        out_p = os.path.join(output_dir, f"{name}.wav")
        # 转回 [samples, channels] 并保存
        sf.write(out_p, tensor.cpu().numpy().T, sr)
        print(f"  ✅ 导出资产: {out_p}")

if __name__ == "__main__":
    run_robust_separation()

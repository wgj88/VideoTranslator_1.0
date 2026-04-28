# -*- coding: utf-8 -*-
import os, torch, numpy as np, subprocess
import soundfile as sf
from pyannote.audio import Model, Inference

def capture():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model_dir = r"E:\VideoTranslator_Project\models\pyannote"
    model = Model.from_pretrained(model_dir)
    model.to(device)
    
    inference = Inference(model, device=device)
    v_src = r"C:\Users\Administrator\separated_audio\pure_vocals.wav"
    
    print("[Action] 正在启动【全内存模式】声纹深度扫描...")
    # --- 核心加固：手动加载，物理绕过坏掉的解码器 ---
    wav, sr = sf.read(v_src)
    if len(wav.shape) == 1: wav = np.expand_dims(wav, axis=0)
    else: wav = wav.T
    payload = {"waveform": torch.from_numpy(wav).float(), "sample_rate": sr}
    
    res = inference(payload)
    data = res.data 
    
    ffmpeg = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
    
    for i in range(data.shape[1]):
        probs = data[:, i]
        max_p = np.max(probs)
        peak_idx = np.argmax(probs)
        peak_time = res.sliding_window[peak_idx].middle
        
        out_wav = f"E:\\VideoTranslator_Project\\separated_audio\\slot_{i}_audition.wav"
        subprocess.run([ffmpeg, "-y", "-i", v_src, "-ss", str(max(0, peak_time-2)), "-t", "4", out_wav], capture_output=True)
        print(f"角色槽位 [{i}]: 自信度 {max_p:.2f}，采样位置 {peak_time:.1f}s -> {out_wav}")

if __name__ == "__main__":
    capture()

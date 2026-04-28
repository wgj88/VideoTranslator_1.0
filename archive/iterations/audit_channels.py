# -*- coding: utf-8 -*-
import os, torch, numpy as np
import soundfile as sf
from pyannote.audio import Model, Inference

def audit_channels():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model_dir = r"E:\VideoTranslator_Project\models\pyannote"
    model = Model.from_pretrained(model_dir)
    model.to(device)
    
    v_src = r"C:\Users\Administrator\separated_audio\pure_vocals.wav"
    inference = Inference(model, device=device)
    
    print("[Audit] 正在全速扫描所有声纹频道...")
    # 手动加载，避开 AudioDecoder
    wav, sr = sf.read(v_src)
    if len(wav.shape) == 1: wav = np.expand_dims(wav, axis=0)
    else: wav = wav.T
    payload = {"waveform": torch.from_numpy(wav).float(), "sample_rate": sr}
    
    segmentation = inference(payload)
    data = segmentation.data # (Frames, 3)
    
    print("\n" + "="*40)
    print("🕵️ 声纹通道活跃度审计")
    print("="*40)
    
    ffmpeg = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
    
    for i in range(data.shape[1]):
        probs = data[:, i]
        max_p = np.max(probs)
        mean_p = np.mean(probs)
        
        print(f"通道_{i}: 最大概率 {max_p:.2f} | 平均概率 {mean_p:.4f}")
        
        # 只要最大概率超过 0.1，我们就认为可能有人说话
        if max_p > 0.1:
            peak_idx = np.argmax(probs)
            peak_time = segmentation.sliding_window[peak_idx].middle
            print(f"  -> 巅峰时刻: {peak_time:.2f}s")
            
            # 物理提取
            out_wav = f"E:\\VideoTranslator_Project\\separated_audio\\audit_channel_{i}.wav"
            import subprocess
            subprocess.run([ffmpeg, "-y", "-i", v_src, "-ss", str(max(0, peak_time-2)), "-t", "4", out_wav], capture_output=True)
            print(f"  -> 样本已生成: {out_wav}")

if __name__ == "__main__":
    audit_channels()

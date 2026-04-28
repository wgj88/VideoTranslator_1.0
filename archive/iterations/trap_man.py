# -*- coding: utf-8 -*-
import os, torch, numpy as np, json, subprocess
import soundfile as sf
from pyannote.audio import Model, Inference

def trap_man_at_20s():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = Model.from_pretrained(r"E:\VideoTranslator_Project\models\pyannote")
    model.to(device)
    inference = Inference(model, device=device)
    v_src = r"C:\Users\Administrator\separated_audio\pure_vocals.wav"
    
    wav, sr = sf.read(v_src)
    # 截取 20s - 30s 的张量
    start_frame = int(20 * sr)
    end_frame = int(30 * sr)
    snippet = wav[start_frame:end_frame]
    
    if len(snippet.shape) == 1: snippet = np.expand_dims(snippet, axis=0)
    else: snippet = snippet.T
    payload = {"waveform": torch.from_numpy(snippet).float(), "sample_rate": sr}
    
    print("[Trap] 正在深度扫描 20s - 30s 片段...")
    res = inference(payload)
    data = res.data.reshape(-1, 3) # 3 个槽位
    
    ffmpeg = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
    
    # 统计这 10 秒内各通道的表现
    for i in range(3):
        probs = data[:, i]
        max_p = np.max(probs)
        if max_p > 0.1:
            peak_idx = np.argmax(probs)
            # 这里的 peak_time 是相对于 20s 的偏移
            peak_time_in_snippet = peak_idx * (10.0 / len(probs))
            abs_time = 20.0 + peak_time_in_snippet
            
            out_wav = f"E:\\VideoTranslator_Project\\separated_audio\\TRAPPED_SPEAKER_SLOT_{i}.wav"
            subprocess.run([ffmpeg, "-y", "-i", v_src, "-ss", str(max(0, abs_time-1.5)), "-t", "3", out_wav], capture_output=True)
            print(f"✅ 捕获成功！槽位 [{i}] 在 {abs_time:.2f}s 活跃，采样已导出。")

if __name__ == "__main__":
    trap_man_at_20s()

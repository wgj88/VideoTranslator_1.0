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
    
    wav, sr = sf.read(v_src)
    if len(wav.shape) == 1: wav = np.expand_dims(wav, axis=0)
    else: wav = wav.T
    payload = {"waveform": torch.from_numpy(wav).float(), "sample_rate": sr}
    
    # 获取原始 3D 矩阵 (Chunks, Frames, Speakers)
    res = inference(payload)
    data = res.data 
    print(f"[Audit] 原始矩阵形状: {data.shape}")
    
    ffmpeg = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
    
    # 核心修正：只遍历最后一个维度 (3 个槽位)
    num_speakers = data.shape[2]
    for i in range(num_speakers):
        # 将所有 Chunk 合并，看这个 Speaker 在全篇的最高概率
        speaker_probs = data[:, :, i]
        max_p = np.max(speaker_probs)
        
        if max_p > 0.1:
            # 找到全篇最高点
            idx = np.unravel_index(np.argmax(speaker_probs), speaker_probs.shape)
            chunk_idx, frame_idx = idx
            
            # 计算该点在全局的时间戳
            # 这里的计算比较复杂，我们简单取 chunk 的中点
            chunk_duration = 5.0 # Pyannote 默认窗口通常是 5s 或 10s
            step = 0.5 # 步长
            global_time = chunk_idx * step + (frame_idx / 589.0) * 2.0 # 估算值
            
            out_wav = f"E:\\VideoTranslator_Project\\separated_audio\\REAL_SLOT_{i}.wav"
            subprocess.run([ffmpeg, "-y", "-i", v_src, "-ss", str(max(0, global_time-2)), "-t", "4", out_wav], capture_output=True)
            print(f"✅ 锁定角色槽位 [{i}]: 最高自信度 {max_p:.2f}，位于 {global_time:.2f}s -> {out_wav}")

if __name__ == "__main__":
    capture()

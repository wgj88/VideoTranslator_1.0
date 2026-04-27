# -*- coding: utf-8 -*-
import os, torch, numpy as np
import soundfile as sf
from pyannote.audio import Model, Inference

def final_audit(audio_path):
    local_model_dir = r"E:\VideoTranslator_Project\models\pyannote"
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    print(f"[Audit] 正在从目录标准加载: {local_model_dir}")
    # 根据官方规范，直接指向文件夹
    model = Model.from_pretrained(local_model_dir)
    model.to(device)
    model.eval()
    
    # 手动加载音频，避开 AudioDecoder Bug
    wav_data, sr = sf.read(audio_path)
    if len(wav_data.shape) == 1: wav_data = np.expand_dims(wav_data, axis=0)
    else: wav_data = wav_data.T
    audio_payload = {"waveform": torch.from_numpy(wav_data).float(), "sample_rate": sr}
    
    inference = Inference(model, device=device)
    segmentation = inference(audio_payload)
    
    data = np.squeeze(segmentation.data)
    print(f"\n[Result] 扫描成功！数据形状: {data.shape}")
    
    # 彻底查清：哪几个通道有除了主讲人之外的声音
    for i in range(data.shape[1]):
        max_p = np.max(data[:, i])
        if max_p > 0.1: # 只要有 10% 的迹象就抓出来
            print(f"  -> 探测到潜在说话人通道 [{i}]: 最高自信度 {max_p:.2f}")

if __name__ == "__main__":
    v_src = r"C:\Users\Administrator\separated_audio\pure_vocals.wav"
    final_audit(v_src)

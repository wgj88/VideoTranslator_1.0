# -*- coding: utf-8 -*-
import os, torch, numpy as np
import soundfile as sf
from pyannote.audio import Model, Inference

def audit_dimensions(audio_path):
    local_model_dir = r"E:\VideoTranslator_Project\models\pyannote"
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # --- 核心修复：允许加载受限权重 ---
    model = Model.from_pretrained(os.path.join(local_model_dir, "config.yaml"))
    weights = torch.load(os.path.join(local_model_dir, "pytorch_model.bin"), map_location=device, weights_only=False)
    model.load_state_dict(weights)
    model.to(device)
    
    wav_data, sr = sf.read(audio_path)
    if len(wav_data.shape) == 1: wav_data = np.expand_dims(wav_data, axis=0)
    else: wav_data = wav_data.T
    audio_payload = {"waveform": torch.from_numpy(wav_data).float(), "sample_rate": sr}
    
    inference = Inference(model, device=device)
    segmentation = inference(audio_payload)
    
    data = np.squeeze(segmentation.data)
    print(f"\n[Audit] 成功加载！数据形状: {data.shape}")
    
    # 彻底查清哪几个通道有声音
    max_probs = np.max(data, axis=0)
    print(f"[Audit] 7个声纹通道的最高自信度: {max_probs}")
    
    # 关键：寻找除了主讲人之外，排名第二的活跃角色
    # 如果 SPEAKER_00 的最高自信度是 0.9，我们找 0.5 左右的那个隐藏角色
    active_channels = np.where(max_probs > 0.2)[0]
    print(f"[Audit] 自信度超过 0.2 的通道 ID: {active_channels}")

if __name__ == "__main__":
    v_src = r"C:\Users\Administrator\separated_audio\pure_vocals.wav"
    audit_dimensions(v_src)

# -*- coding: utf-8 -*-
import os, torch, numpy as np
import soundfile as sf
from pyannote.audio.models.segmentation import PyanNet
from pyannote.audio import Inference

def manual_audit(audio_path):
    local_model_dir = r"E:\VideoTranslator_Project\models\pyannote"
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    print("[Audit] 正在手动实例化 PyanNet 架构...")
    model = PyanNet(
        sample_rate=16000,
        num_channels=1,
        sincnet={'stride': 10},
        lstm={'hidden_size': 128, 'num_layers': 4, 'bidirectional': True},
        linear={'hidden_size': 128, 'num_layers': 2}
    )
    
    print("[Audit] 正在物理加载权重...")
    weights = torch.load(os.path.join(local_model_dir, "pytorch_model.bin"), map_location=device, weights_only=False)
    if "state_dict" in weights: weights = weights["state_dict"]
    
    model.load_state_dict(weights, strict=False)
    model.to(device)
    model.eval()
    
    wav_data, sr = sf.read(audio_path)
    if len(wav_data.shape) == 1: wav_data = np.expand_dims(wav_data, axis=0)
    else: wav_data = wav_data.T
    audio_payload = {"waveform": torch.from_numpy(wav_data).float(), "sample_rate": sr}
    
    inference = Inference(model, device=device)
    segmentation = inference(audio_payload)
    
    data = np.squeeze(segmentation.data)
    print(f"\n[Result] 审计完成！数据形状: {data.shape}")
    
    # 全通道扫描：找出所有具备说话特征的通道
    for i in range(data.shape[1]):
        max_p = np.max(data[:, i])
        if max_p > 0.05:
            # 活跃帧数统计
            active_count = np.sum(data[:, i] > 0.2)
            if active_count > 10:
                print(f"  -> 发现活跃声纹通道 [{i}]:")
                print(f"     - 最高自信度: {max_p:.2f}")
                print(f"     - 预估累计时长: {active_count * 0.016:.1f} 秒")

if __name__ == "__main__":
    v_src = r"C:\Users\Administrator\separated_audio\pure_vocals.wav"
    manual_audit(v_src)

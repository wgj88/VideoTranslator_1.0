# -*- coding: utf-8 -*-
import os, torch, numpy as np, json
import soundfile as sf
from pyannote.audio import Model, Inference
from sklearn.cluster import KMeans
from pyannote.core import Annotation, Segment

def audit_full_timeline():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = Model.from_pretrained(r"E:\VideoTranslator_Project\models\pyannote")
    model.to(device)
    inference = Inference(model, device=device)
    v_src = r"C:\Users\Administrator\separated_audio\pure_vocals.wav"
    
    wav, sr = sf.read(v_src)
    if len(wav.shape) == 1: wav = np.expand_dims(wav, axis=0)
    else: wav = wav.T
    payload = {"waveform": torch.from_numpy(wav).float(), "sample_rate": sr}
    
    res = inference(payload)
    data = res.data.reshape(-1, 3)
    
    active_mask = np.max(data, axis=1) > 0.2
    kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
    labels = kmeans.fit_predict(data[active_mask])
    
    annotation = Annotation()
    full_labels = np.zeros(len(data), dtype=int) - 1
    full_labels[active_mask] = labels
    
    frame_dur = 147.9 / len(data)
    
    print("\n" + "="*50)
    print("📈 全篇 147.9 秒声纹足迹追踪")
    print("="*50)

    # 统计每个时间段的活跃角色
    # 我们每 20 秒报一次账
    for t in range(0, 140, 20):
        start_frame = int(t / frame_dur)
        end_frame = int((t + 20) / frame_dur)
        segment_labels = full_labels[start_frame:end_frame]
        present_roles = set()
        for l in segment_labels:
            if l != -1: present_roles.add(f"SPEAKER_{l:02d}")
        print(f"[{t:03d}s - {t+20:03d}s] 活跃角色: {present_roles}")

    # 抽取视频最后 20 秒的一个样本！
    ffmpeg = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
    # 寻找最后 20 秒内属于 SPEAKER_01 的时刻
    end_mask = full_labels[int(120/frame_dur):]
    if 1 in end_mask:
        last_idx = np.where(full_labels == 1)[0][-1]
        last_time = last_idx * frame_dur
        out_wav = r"E:\VideoTranslator_Project\separated_audio\END_SECTION_SPEAKER_01.wav"
        import subprocess
        subprocess.run([ffmpeg, "-y", "-i", v_src, "-ss", str(max(0, last_time-4)), "-t", "4", out_wav], capture_output=True)
        print(f"\n📢 已从视频【结尾处】(约 {last_time:.1f}s) 提取 SPEAKER_01 的样本：{out_wav}")

if __name__ == "__main__":
    audit_full_timeline()

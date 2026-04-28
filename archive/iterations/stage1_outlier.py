# -*- coding: utf-8 -*-
import os, torch, numpy as np, subprocess, json
import soundfile as sf
from speechbrain.inference.speaker import EncoderClassifier
from sklearn.cluster import AgglomerativeClustering

def find_the_outlier():
    device_str = "cuda:0" if torch.cuda.is_available() else "cpu"
    device = torch.device(device_str)
    
    v_src = r"C:\Users\Administrator\separated_audio\pure_vocals.wav"
    print(f"[NuclearScan] 正在启动声纹显微镜 (GPU: {device_str})...")
    
    encoder = EncoderClassifier.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb", run_opts={"device": device_str})
    
    # --- 1. 使用 soundfile 稳健读取 ---
    wav_data, sr = sf.read(v_src)
    if len(wav_data.shape) > 1: wav_data = np.mean(wav_data, axis=1) # 合并声道
    
    # 物理降采样到 16k (SpeechBrain 唯一认证频率)
    import scipy.signal as signal
    samples_16k = int(len(wav_data) * 16000 / sr)
    wav_16k = signal.resample(wav_data, samples_16k)
    
    # 2. 地毯式大采样
    embeddings = []
    time_stamps = []
    step = 16000 # 1s 步长
    window = 32000 # 2s 窗口
    
    print("  -> 正在进行 192 维全息声纹提取...")
    for i in range(0, len(wav_16k) - window, step):
        snippet = wav_16k[i : i + window]
        # 强制格式为 [1, window]
        snippet_torch = torch.from_numpy(snippet).float().unsqueeze(0).to(device)
        
        with torch.no_grad():
            emb = encoder.encode_batch(snippet_torch)
            embeddings.append(emb.cpu().numpy().flatten())
            time_stamps.append(i / 16000)
            
    embeddings = np.array(embeddings)
    
    # 3. 聚类分析：寻找 4 个声纹族群
    print(f"  -> 采样完成 (共 {len(embeddings)} 组特征)。执行 4 角色物理聚类...")
    clusterer = AgglomerativeClustering(n_clusters=4)
    labels = clusterer.fit_predict(embeddings)
    
    ffmpeg = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
    for l in range(4):
        indices = np.where(labels == l)[0]
        if len(indices) == 0: continue
        t = time_stamps[indices[len(indices)//2]]
        out_wav = f"E:\\VideoTranslator_Project\\output_final\\OUTLIER_SCAN_SPK_{l}.wav"
        subprocess.run([ffmpeg, "-y", "-i", v_src, "-ss", str(max(0, t-1)), "-t", "5", out_wav], capture_output=True)
        print(f"✅ 捕获到声纹群组 {l}: 样板导出至 {out_wav}")

if __name__ == "__main__":
    find_the_outlier()

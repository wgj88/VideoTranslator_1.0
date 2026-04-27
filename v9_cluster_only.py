# -*- coding: utf-8 -*-
import os, sys, json, torch, numpy as np
import soundfile as sf
import torchaudio.transforms as T
from speechbrain.inference.speaker import EncoderClassifier
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import silhouette_score
import re

def run_cluster_only():
    v_src = r"C:\Users\Administrator\separated_audio\pure_vocals.wav"
    asr_json = r"E:\VideoTranslator_Project\separated_audio\v9_asr_temp.json"
    device_str = "cuda:0"
    
    print("[CLUSTER_ONLY] 正在加载声纹特征模型...")
    encoder = EncoderClassifier.from_hparams(
        source="speechbrain/spkrec-ecapa-voxceleb", 
        run_opts={"device": device_str}
    )

    # 物理读取
    wav_data, sr_orig = sf.read(v_src)
    if len(wav_data.shape) > 1: wav_data = np.mean(wav_data, axis=1)
    wav_torch = torch.from_numpy(wav_data).float().unsqueeze(0)
    resampler = T.Resample(sr_orig, 16000)
    wav_16k = resampler(wav_torch)

    with open(asr_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    embeddings = []
    valid_indices = []
    
    print(f"[CLUSTER_ONLY] 正在对 {len(data)} 个片段进行声纹采样...")
    for i, seg in enumerate(data):
        start_p, end_p = int(seg['start'] * 16000), int(seg['end'] * 16000)
        snippet = wav_16k[:, start_p:end_p]
        
        if snippet.shape[1] < 1600: continue # 忽略过短片段
        
        with torch.no_grad():
            emb = encoder.encode_batch(snippet.to(device_str))
            embeddings.append(emb.cpu().numpy().flatten())
            valid_indices.append(i)
            
    embeddings = np.array(embeddings)
    
    # 自动聚类逻辑
    print("[CLUSTER_ONLY] 正在进行凝聚层次聚类 (寻找最佳分堆)...")
    best_n = 2
    best_score = -1
    for n in range(2, min(5, len(embeddings))):
        clusterer = AgglomerativeClustering(n_clusters=n)
        labels = clusterer.fit_predict(embeddings)
        score = silhouette_score(embeddings, labels)
        print(f"  * 方案: {n} 角色 | 得分: {score:.4f}")
        if score > best_score:
            best_score = score
            best_n = n

    print(f"🏆 算法定论：该视频中有 {best_n} 个主要角色。")
    final_labels = AgglomerativeClustering(n_clusters=best_n).fit_predict(embeddings)
    
    for idx, label in zip(valid_indices, final_labels):
        data[idx]['speaker'] = f"SPEAKER_{label:02d}"

    out_json = r"E:\VideoTranslator_Project\separated_audio\v9_final_script.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ 聚类阶段完成：{out_json}")

if __name__ == "__main__":
    run_cluster_only()

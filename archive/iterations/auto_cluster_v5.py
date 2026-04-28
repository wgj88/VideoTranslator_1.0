# -*- coding: utf-8 -*-
import os, torch, numpy as np, json
import soundfile as sf
from pyannote.audio import Model, Inference
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import silhouette_score

class AutoDiarizer:
    def __init__(self, model_dir=r"E:\VideoTranslator_Project\models\pyannote"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = Model.from_pretrained(model_dir)
        self.model.to(self.device)

    def run_autonomous_clustering(self, audio_path):
        print(f"\n[AI] 正在对全篇进行“零干预”声纹大数据分析...")
        
        # 1. 提取每一帧的原始声纹概率
        inference = Inference(self.model, device=self.device)
        wav, sr = sf.read(audio_path)
        if len(wav.shape) == 1: wav = np.expand_dims(wav, axis=0)
        else: wav = wav.T
        payload = {"waveform": torch.from_numpy(wav).float(), "sample_rate": sr}
        
        res = inference(payload)
        data = res.data.reshape(-1, res.data.shape[2]) # (Frames, 3)
        
        # 2. 物理降噪：只取有声音的特征点
        active_mask = np.max(data, axis=1) > 0.15
        features = data[active_mask]
        
        # 3. 寻找最佳聚类数 (从 2 到 4 自动尝试)
        print("  -> 正在计算最佳角色分布方案...")
        best_n = 2
        best_score = -1
        
        # 采样 1000 个点进行快速计算
        if len(features) > 2000:
            sample_idx = np.linspace(0, len(features)-1, 2000, dtype=int)
            calc_features = features[sample_idx]
        else:
            calc_features = features

        for n in range(2, 5):
            clusterer = AgglomerativeClustering(n_clusters=n)
            labels = clusterer.fit_predict(calc_features)
            score = silhouette_score(calc_features, labels)
            if score > best_score:
                best_score = score
                best_n = n
        
        print(f"🏆 算法定论：该视频中最可能有 {best_n} 个说话角色。")
        
        # 4. 执行正式聚类
        final_clusterer = AgglomerativeClustering(n_clusters=best_n)
        final_labels = final_clusterer.fit_predict(features)
        
        # 5. 汇报全自动结果
        results = {}
        for l in range(best_n):
            count = np.sum(final_labels == l)
            results[f"SPEAKER_{l:02d}"] = count * 0.016 # 估算时长
            
        return results

if __name__ == "__main__":
    v_src = r"C:\Users\Administrator\separated_audio\pure_vocals.wav"
    ad = AutoDiarizer()
    report = ad.run_autonomous_clustering(v_src)
    print("\n全自动审计结果：")
    for spk, dur in report.items():
        print(f"- {spk}: 预估戏份 {dur:.2f} 秒")

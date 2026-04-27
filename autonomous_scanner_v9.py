# -*- coding: utf-8 -*-
import os, sys, json, torch, whisperx, numpy as np
import soundfile as sf
import torchaudio.transforms as T
from speechbrain.inference.speaker import EncoderClassifier
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import silhouette_score

# --- 环境加固 ---
ffmpeg_dir = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32"
os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ["PATH"]

def run_v9_autonomous_scanner():
    device_str = "cuda:0" if torch.cuda.is_available() else "cpu"
    device = torch.device(device_str)
    v_src = r"C:\Users\Administrator\separated_audio\pure_vocals.wav"
    
    print(f"\n[V9.0 Scanner] 正在初始化“声纹全景扫描仪” (设备: {device_str})...")

    # 1. 极速听译与单词对齐
    # 使用 WhisperX 建立基准剧本
    asr_model = whisperx.load_model("base", "cuda", compute_type="float16")
    audio = whisperx.load_audio(v_src)
    result = asr_model.transcribe(audio, batch_size=16)
    
    print("  -> 正在进行毫秒级时间轴纠偏...")
    model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device_str)
    aligned_result = whisperx.align(result["segments"], model_a, metadata, audio, device_str, return_char_alignments=False)
    
    del asr_model, model_a
    torch.cuda.empty_cache()

    # 2. 角色画像提取 (SpeechBrain Embedding)
    print("  -> 正在为全篇提取声纹指纹向量...")
    encoder = EncoderClassifier.from_hparams(
        source="speechbrain/spkrec-ecapa-voxceleb", 
        run_opts={"device": device_str}
    )
    
    # 物理读取并重采样到 16k
    wav_data, sr_orig = sf.read(v_src)
    if len(wav_data.shape) > 1: wav_data = np.mean(wav_data, axis=1)
    wav_torch = torch.from_numpy(wav_data).float().unsqueeze(0)
    resampler = T.Resample(sr_orig, 16000)
    wav_16k = resampler(wav_torch)

    embeddings = []
    valid_segments = []
    
    for seg in aligned_result['segments']:
        s, e = int(seg['start'] * 16000), int(seg['end'] * 16000)
        snippet = wav_16k[:, s:e]
        if snippet.shape[1] < 3200: continue # 忽略短于 0.2s 的碎片
        
        with torch.no_grad():
            emb = encoder.encode_batch(snippet.to(device))
            embeddings.append(emb.cpu().numpy().flatten())
            valid_segments.append(seg)

    embeddings = np.array(embeddings)
    print(f"  -> 特征提取完成。样本总数: {len(embeddings)}")

    # 3. 凝聚聚类：自动寻找最优人数
    print("  -> 正在通过数学算法分析视频角色分布...")
    best_n = 2
    best_score = -1
    
    # 尝试 2 到 4 个人选
    for n in range(2, min(5, len(embeddings))):
        clusterer = AgglomerativeClustering(n_clusters=n)
        labels = clusterer.fit_predict(embeddings)
        score = silhouette_score(embeddings, labels)
        print(f"     * 评估 {n} 角色方案 -> 纯度得分: {score:.4f}")
        if score > best_score:
            best_score = score
            best_n = n

    print(f"🏆 算法定论：视频包含 {best_n} 个主要说话人。正在执行最终标记...")
    final_clusterer = AgglomerativeClustering(n_clusters=best_n)
    final_labels = final_clusterer.fit_predict(embeddings)

    # 4. 产出精标角色剧本
    for seg, label in zip(valid_segments, final_labels):
        seg['speaker'] = f"SPEAKER_{label:02d}"

    json_out = r"E:\VideoTranslator_Project\separated_audio\V9_AUTONOMOUS_SCRIPT.json"
    with open(json_out, "w", encoding="utf-8") as f:
        json.dump(aligned_result['segments'], f, ensure_ascii=False, indent=2)
    
    print(f"✅ V9.0 剧本生成成功！路径: {json_out}")
    return json_out

if __name__ == "__main__":
    run_v9_autonomous_scanner()

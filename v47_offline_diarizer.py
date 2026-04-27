# -*- coding: utf-8 -*-
import os, sys, json, torch, whisper, numpy as np
import soundfile as sf
import torchaudio.transforms as T

def run_offline_diarization():
    vocals_wav = r"E:\VideoTranslator_Project\unhinged_tech\separated\vocals.wav"
    output_json = r"E:\VideoTranslator_Project\unhinged_tech\offline_diarization.json"
    
    print("\n[Offline-Diarizer] 正在启动全离线审计模式...")
    
    # 1. 物理读取音频
    wav_data, sr_orig = sf.read(vocals_wav)
    if len(wav_data.shape) > 1: wav_data = np.mean(wav_data, axis=1)
    
    # 2. 极速听译 (使用本地已有的 Whisper base)
    print("  -> Step 1: 正在生成剧本初稿 (OpenAI Whisper)...")
    asr_model = whisper.load_model("base")
    # Whisper 期望 f32 numpy
    res = asr_model.transcribe(wav_data.astype(np.float32), verbose=False)
    
    # 3. 声纹提取 (SpeechBrain)
    print("  -> Step 2: 正在提取声纹指纹 (SpeechBrain)...")
    from speechbrain.inference.speaker import EncoderClassifier
    encoder = EncoderClassifier.from_hparams(
        source="speechbrain/spkrec-ecapa-voxceleb",
        run_opts={"device": "cuda"}
    )
    
    wav_torch = torch.from_numpy(wav_data).float().unsqueeze(0)
    resampler = T.Resample(sr_orig, 16000)
    
    embeddings = []
    valid_indices = []
    
    print(f"  -> 正在处理 {len(res['segments'])} 个对话片段...")
    for i, seg in enumerate(res['segments']):
        s_p, e_p = int(seg['start'] * sr_orig), int(seg['end'] * sr_orig)
        snippet = wav_torch[:, s_p:e_p]
        if snippet.shape[1] < sr_orig * 0.4: continue
        
        snippet_16k = resampler(snippet)
        with torch.no_grad():
            emb = encoder.encode_batch(snippet_16k.to("cuda"))
            embeddings.append(emb.cpu().numpy().flatten())
            valid_indices.append(i)

    if not embeddings:
        print("❌ 未能提取到有效的声纹特征")
        return

    # 4. 自动聚类
    from sklearn.cluster import AgglomerativeClustering
    embeddings = np.array(embeddings)
    # 针对 9 分钟视频，我们尝试 2-6 人
    clusterer = AgglomerativeClustering(n_clusters=None, distance_threshold=0.8) # 自动判定人数
    labels = clusterer.fit_predict(embeddings)
    
    num_speakers = len(np.unique(labels))
    print(f"🏆 审计定论：共发现 {num_speakers} 个独立角色。")
    
    for idx, label in zip(valid_indices, labels):
        res['segments'][idx]['speaker'] = f"SPEAKER_{label:02d}"
    
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(res['segments'], f, ensure_ascii=False, indent=2)
    
    print(f"✅ 审计完成！剧本归档至: {output_json}")

if __name__ == "__main__":
    run_offline_diarization()

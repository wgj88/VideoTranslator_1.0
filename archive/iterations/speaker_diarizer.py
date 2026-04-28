# -*- coding: utf-8 -*-
import os, json, torch, whisperx, numpy as np
import pandas as pd
import soundfile as sf
import torchaudio.transforms as T

class SpeakerDiarizer:
    def __init__(self, local_model_dir=r"E:\VideoTranslator_Project\models\pyannote"):
        ffmpeg_dir = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32"
        os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ["PATH"]
        self.device_str = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.device = torch.device(self.device_str)
        print(f"[Diarizer] 正在启动【彻底绕过 torchcodec】的稳健引擎...")

    def process_autonomous(self, audio_path):
        print(f"\n[Diarizer] 正在执行全自动声纹分割...")
        
        # 1. 极速听译
        comp_type = "float16" if "cuda" in self.device_str else "int8"
        asr_model = whisperx.load_model("base", "cuda", compute_type=comp_type)
        audio_array = whisperx.load_audio(audio_path)
        result = asr_model.transcribe(audio_array, batch_size=16)
        del asr_model
        torch.cuda.empty_cache()

        # 2. 加载声纹提取器
        from speechbrain.inference.speaker import EncoderClassifier
        encoder = EncoderClassifier.from_hparams(
            source="speechbrain/spkrec-ecapa-voxceleb", 
            run_opts={"device": self.device_str}
        )

        # 3. 内存级特征提取 (避开 torchaudio.load)
        print(f"  -> 正在为 {len(result['segments'])} 个片段提取声纹基因...")
        # A. 使用 soundfile 稳健加载
        wav_data, sr_orig = sf.read(audio_path)
        # B. 转为 torch 张量 [1, samples]
        if len(wav_data.shape) > 1: # Stereo to Mono
            wav_data = np.mean(wav_data, axis=1)
        wav_torch = torch.from_numpy(wav_data).float().unsqueeze(0)
        
        # C. 准备 16k 重采样器
        resampler = T.Resample(sr_orig, 16000)
        
        embeddings = []
        valid_indices = []
        for i, seg in enumerate(result['segments']):
            s_p, e_p = int(seg['start'] * sr_orig), int(seg['end'] * sr_orig)
            snippet = wav_torch[:, s_p:e_p]
            
            if snippet.shape[1] < sr_orig * 0.3: continue # 忽略过短片段
            
            # 降采样并提取
            snippet_16k = resampler(snippet)
            with torch.no_grad():
                emb = encoder.encode_batch(snippet_16k.to(self.device))
                embeddings.append(emb.cpu().numpy().flatten())
                valid_indices.append(i)
        
        if not embeddings: return None
        embeddings = np.array(embeddings)

        # 4. 自动聚类 (从 2 人开始尝试)
        from sklearn.cluster import AgglomerativeClustering
        from sklearn.metrics import silhouette_score
        
        best_n = 2
        best_score = -1
        # 针对 2.5 分钟视频，我们合理尝试 2-3 人
        for n in range(2, min(4, len(embeddings))):
            clusterer = AgglomerativeClustering(n_clusters=n)
            labels = clusterer.fit_predict(embeddings)
            score = silhouette_score(embeddings, labels)
            print(f"     * 尝试 {n} 角色方案 -> 相似度得分: {score:.4f}")
            if score > best_score:
                best_score = score
                best_n = n
        
        print(f"🏆 算法定论：此视频中有 {best_n} 个说话角色。")
        final_labels = AgglomerativeClustering(n_clusters=best_n).fit_predict(embeddings)
        
        for idx, label in zip(valid_indices, final_labels):
            result['segments'][idx]['speaker'] = f"SPEAKER_{label:02d}"

        json_out = audio_path.replace(".wav", "_v6_final_script.json")
        with open(json_out, "w", encoding="utf-8") as f:
            json.dump(result['segments'], f, ensure_ascii=False, indent=2)
            
        return json_out

if __name__ == "__main__":
    sd = SpeakerDiarizer()
    v_src = r"C:\Users\Administrator\separated_audio\pure_vocals.wav"
    sd.process_autonomous(v_src)

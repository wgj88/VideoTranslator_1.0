# -*- coding: utf-8 -*-
import os, sys, json, torch, whisper
from pyannote.audio import Pipeline

def run_unhinged_diarization():
    vocals_wav = r"E:\VideoTranslator_Project\unhinged_tech\separated\vocals.wav"
    output_json = r"E:\VideoTranslator_Project\unhinged_tech\diarization_map.json"
    model_dir = r"E:\VideoTranslator_Project\models\pyannote"
    
    print("\n[Diarizer] 正在对 9 分钟长视频执行【声纹指纹大审计】...")
    
    # 1. 角色分离 (Diarization)
    # 注意：我们这里使用本地权重，避开网络重载
    pipeline = Pipeline.from_pretrained(os.path.join(model_dir, "config.yaml"))
    pipeline.to(torch.device("cuda"))
    
    print("  -> 正在计算声纹聚类 (Clustering)...")
    diarization = pipeline(vocals_wav)
    
    diarization_data = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        diarization_data.append({
            "start": round(turn.start, 3),
            "end": round(turn.end, 3),
            "speaker": speaker
        })
    
    # 2. 剧本初探 (ASR)
    print("  -> 正在同步生成 ASR 原始剧本...")
    model = whisper.load_model("base")
    res = model.transcribe(vocals_wav)
    
    full_result = {
        "diarization": diarization_data,
        "segments": res['segments']
    }
    
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(full_result, f, indent=2)
    
    print(f"\n🏆 声纹地图已绘制完成！发现角色数量：{len(set(d['speaker'] for d in diarization_data))}")
    print(f"📂 剧本文件：{output_json}")

if __name__ == "__main__":
    run_unhinged_diarization()

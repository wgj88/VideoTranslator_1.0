# -*- coding: utf-8 -*-
import os, torch, whisper, json, soundfile as sf
from pyannote.audio import Pipeline

def run_v2():
    vocals_wav = r"E:\VideoTranslator_Project\unhinged_tech\separated\vocals.wav"
    output_json = r"E:\VideoTranslator_Project\unhinged_tech\diarization_map.json"
    
    print("\n[Diarizer-V2] 正在通过【内存张量注入】模式启动审计...")
    
    # 1. 物理读取信号 (避开所有解码库)
    wav, sr = sf.read(vocals_wav)
    if wav.ndim > 1: wav = wav.mean(axis=1) # 转单声道
    
    # 转为 pyannote 期望的 [1, samples] 格式
    waveform = torch.from_numpy(wav[None, :]).float()
    audio_in_memory = {"waveform": waveform, "sample_rate": sr}
    
    # 2. 启动 Pipeline
    print("  -> 正在加载声纹聚类模型 (SD-3.1)...")
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=False) # 假设已缓存
    pipeline.to(torch.device("cuda"))
    
    # 3. 执行识别
    print("  -> 正在全速审计 9 分钟声纹 (GPU:0)...")
    diarization = pipeline(audio_in_memory)
    
    diarization_data = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        diarization_data.append({"start": turn.start, "end": turn.end, "speaker": speaker})
    
    # 4. ASR 剧本 (同步执行)
    print("  -> 正在生成 ASR 剧本初稿...")
    model = whisper.load_model("base")
    # 注意：Whisper 也用内存张量比较快
    res = model.transcribe(wav.astype(np.float32), verbose=False)
    
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump({"diarization": diarization_data, "segments": res['segments']}, f, indent=2)
    
    print(f"✅ 审计大功告成！文件保存至: {output_json}")

if __name__ == "__main__":
    import numpy as np
    run_v2()

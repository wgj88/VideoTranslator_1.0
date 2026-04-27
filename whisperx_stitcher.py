# -*- coding: utf-8 -*-
import os, sys, json, torch, whisperx, numpy as np
import soundfile as sf
import pandas as pd
from pyannote.audio import Model, Inference

# 物理注入 FFmpeg 路径
ffmpeg_dir = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32"
if ffmpeg_dir not in os.environ["PATH"]:
    os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ["PATH"]

def run_stitcher():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    v_src = r"C:\Users\Administrator\separated_audio\pure_vocals.wav"
    model_dir = r"E:\VideoTranslator_Project\models\pyannote"
    
    print(f"\n[Stitcher] 正在初始化引擎 (设备: {device})...")
    
    # 1. 加载 ASR 和 Align 模型
    # CPU 下使用 int8 保证速度，GPU 下使用 float16
    compute_type = "float16" if device == "cuda" else "int8"
    asr_model = whisperx.load_model("base", device, compute_type=compute_type)
    audio = whisperx.load_audio(v_src)
    
    print("  -> [Step 1] 正在进行毫秒级听译...")
    result = asr_model.transcribe(audio, batch_size=16)
    
    print("  -> [Step 2] 正在执行单词级时间轴对齐...")
    model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
    result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)

    # 2. 本地声纹扫描 (利用内存直供补丁)
    print("  -> [Step 3] 正在利用本地模型执行声纹分割...")
    model = Model.from_pretrained(model_dir)
    inference = Inference(model, device=torch.device(device))
    
    wav_data, sr = sf.read(v_src)
    if len(wav_data.shape) == 1: wav_data = np.expand_dims(wav_data, axis=0)
    else: wav_data = wav_data.T
    audio_payload = {"waveform": torch.from_numpy(wav_data).float(), "sample_rate": sr}
    
    segmentation = inference(audio_payload)
    
    # 3. 概率转 DataFrame
    active_indices = np.argmax(segmentation.data, axis=1).flatten()
    diarize_segments = []
    switches = np.where(np.diff(active_indices) != 0)[0]
    
    start_idx = 0
    for switch_idx in switches:
        diarize_segments.append({
            "start": segmentation.sliding_window[start_idx].start,
            "end": segmentation.sliding_window[switch_idx].end,
            "speaker": f"SPEAKER_{active_indices[start_idx]:02d}"
        })
        start_idx = switch_idx + 1
    diarize_segments.append({
        "start": segmentation.sliding_window[start_idx].start,
        "end": segmentation.sliding_window[-1].end,
        "speaker": f"SPEAKER_{active_indices[start_idx]:02d}"
    })
    
    # 4. 【核心缝合】
    print("  -> [Step 4] 正在执行物理角色缝合...")
    final_result = whisperx.assign_word_speakers(pd.DataFrame(diarize_segments), result)
    
    out_json = r"E:\VideoTranslator_Project\separated_audio\STITCHED_SCRIPT.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(final_result['segments'], f, ensure_ascii=False, indent=2)
        
    print(f"\n🏆 缝合成功！精标剧本已产出: {out_json}")
    
    # 打印前 5 句看看角色分对了没
    for i in range(min(5, len(final_result['segments']))):
        s = final_result['segments'][i]
        print(f"[{s['start']:.1f}s] {s.get('speaker', 'UNK')}: {s['text'][:30]}...")

if __name__ == "__main__":
    run_stitcher()

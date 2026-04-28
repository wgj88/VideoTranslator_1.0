# -*- coding: utf-8 -*-
import os, sys, json, torch, whisperx

# 物理注入路径
os.environ["PATH"] = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32" + os.pathsep + os.environ["PATH"]

def run_asr_only():
    v_src = r"C:\Users\Administrator\separated_audio\pure_vocals.wav"
    device = "cuda"
    
    print("[ASR_ONLY] 正在进行毫秒级听译...")
    # 只加载 ASR 模型
    model = whisperx.load_model("base", device, compute_type="float16")
    audio = whisperx.load_audio(v_src)
    result = model.transcribe(audio, batch_size=16)
    
    print("[ASR_ONLY] 正在进行单词对齐...")
    model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
    result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)
    
    out_json = r"E:\VideoTranslator_Project\separated_audio\v9_asr_temp.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(result['segments'], f, ensure_ascii=False, indent=2)
    print(f"✅ ASR 阶段完成：{out_json}")

if __name__ == "__main__":
    run_asr_only()

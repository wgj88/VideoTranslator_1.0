# -*- coding: utf-8 -*-
import os, sys, json, whisper, torch, soundfile as sf
import numpy as np

work_dir = r"E:\VideoTranslator_Project\FINAL_DUB_TEMP"
seg_0 = os.path.join(work_dir, "pure_zh_0.wav")

def perform_audit():
    print("\n" + "="*50)
    print("🕵️ 原始配音片段审计报告")
    print("="*50)

    if not os.path.exists(seg_0):
        print(f"❌ 错误：找不到文件 {seg_0}")
        return

    # 1. 物理参数审计
    info = sf.info(seg_0)
    print(f"[参数] 采样率: {info.samplerate}Hz, 时长: {info.duration:.2f}s, 通道: {info.channels}")

    # 2. 语种语义审计 (利用 Whisper)
    print("[语义] 正在利用 Whisper 回听第一句配音...")
    model = whisper.load_model("base")
    result = model.transcribe(seg_0)
    
    print(f"[结果] 识别语种: {result['language']}")
    print(f"[结果] 识别内容: {result['text']}")

    # 3. 产生纯净试听大包
    print("\n[Action] 正在合并 8 个片段用于试听...")
    all_audio = []
    for i in range(8):
        p = os.path.join(work_dir, f"pure_zh_{i}.wav")
        if os.path.exists(p):
            data, sr = sf.read(p)
            all_audio.append(data)
    
    combined = np.concatenate(all_audio)
    out_p = r"E:\VideoTranslator_Project\output_final\PURE_DUB_AUDIT.wav"
    sf.write(out_p, combined, sr)
    print(f"✅ 审计音轨已合并：{out_p}")

if __name__ == "__main__":
    perform_audit()

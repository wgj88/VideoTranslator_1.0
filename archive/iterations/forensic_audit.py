# -*- coding: utf-8 -*-
import os, json, sys, whisper
sys.path.append(r"E:\VideoTranslator_Project")

def forensic_audit():
    json_path = r"E:\VideoTranslator_Project\raw_videos\Vlog ｜ New technology paves way for better life at CICPE_zh.json"
    audio_seg_0 = r"E:\VideoTranslator_Project\raw_videos\Vlog ｜ New technology paves way for better life at CICPE_zh_v4_wavs\seg_0.wav"
    
    print("\n" + "="*50)
    print("🕵️ 汉化失踪案：深度声学取证报告")
    print("="*50)

    # 1. 检查 JSON 文本
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"[Step 1] JSON 文本采样: {data[0].get('translated_text')}")

    # 2. 检查生成的音频
    if os.path.exists(audio_seg_0):
        print(f"[Step 2] 发现音频片段: {audio_seg_0}")
        # 使用 Whisper 对配音片段进行“回听”
        model = whisper.load_model("tiny")
        result = model.transcribe(audio_seg_0)
        print(f"[Step 2] AI 回听内容: {result['text']}")
        print(f"[Step 2] AI 识别语种: {result['language']}")
    else:
        print("[Step 2] ❌ 警告：未发现音频片段！")

if __name__ == "__main__":
    forensic_audit()

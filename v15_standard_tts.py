# -*- coding: utf-8 -*-
import os, json, requests, subprocess, numpy as np
import soundfile as sf

def run_standard_tts():
    script_path = r"E:\VideoTranslator_Project\separated_audio\V12_CONSTRAINED_SCRIPT.json"
    dotenv_path = r"C:\Users\Administrator\Desktop\HorrorAgent_Project\.env"
    temp_dir = r"E:\VideoTranslator_Project\temp_factory\v15_std_wavs"
    os.makedirs(temp_dir, exist_ok=True)
    
    # 获取 API Key
    with open(dotenv_path, "r") as f:
        api_key = [l for l in f if "SILICONFLOW_API_KEY" in l][0].split("=")[1].strip().replace('"', '').replace("'", "")

    with open(script_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"\n[V15-Standard] 正在调用硅基流动生成【标准版】语音...")

    valid_segments = []
    # 我们生成前 5 句作为标杆
    for i in range(5):
        item = data[i]
        zh_text = item['zh'].strip()
        
        # 调用标准 TTS API (Fish Speech 1.5)
        # 注意：这里我们不提供 prompt_audio，这就是“标准模式”
        payload = {
            "model": "fishaudio/fish-speech-1.5",
            "text": zh_text,
            "format": "wav",
            "references": [] # 重点：空参考 = 标准语音
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            print(f"  -> 正在生成 Seg_{i}: {zh_text[:10]}...")
            # 注意：SiliconFlow 的 TTS 可能是二进制流或 URL，我们采取稳健处理
            r = requests.post("https://api.siliconflow.cn/v1/tts", json=payload, headers=headers)
            
            out_p = os.path.join(temp_dir, f"std_{i}.wav")
            with open(out_p, "wb") as f_wav:
                f_wav.write(r.content)
            
            valid_segments.append(out_p)
        except Exception as e:
            print(f"     ❌ 失败: {e}")

    # 合并
    output_wav = r"E:\VideoTranslator_Project\output_final\V15_STANDARD_VOICE_VERIFY.wav"
    all_data = []
    for p in valid_segments:
        d, sr = sf.read(p)
        all_data.append(d)
    
    if all_data:
        sf.write(output_wav, np.concatenate(all_data), sr)
        print(f"\n🏆 标准版试听音轨已产出：{output_wav}")

if __name__ == "__main__":
    run_standard_tts()

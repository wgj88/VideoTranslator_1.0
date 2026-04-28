# -*- coding: utf-8 -*-
import requests, json, os

def get_real_translation():
    # 1. 读 Key
    with open(r"C:\Users\Administrator\Desktop\HorrorAgent_Project\.env", "r") as f:
        key = [l for l in f if "SILICONFLOW_API_KEY" in l][0].split("=")[1].strip().split()[0]
    
    # 2. 读 5 句台词
    json_path = r'E:\VideoTranslator_Project\raw_videos\8 EASY Faceless YouTube Channel Ideas for 2026 (High RPM + Views).json'
    with open(json_path, "r", encoding="utf-8-sig") as f:
        data = json.load(f)[:5]

    text = "\n".join([f"{i}: {d['text']}" for i, d in enumerate(data)])
    
    # 3. 调用翻译
    payload = {
        "model": "deepseek-ai/DeepSeek-V3",
        "messages": [{"role": "user", "content": f"请将这些印地语/英语视频台词翻译成地道的中文解说词。返回JSON数组，格式：[{{'idx': 0, 'zh': '...'}}]。\n\n内容：\n{text}"}],
        "response_format": {"type": "json_object"}
    }
    
    r = requests.post("https://api.siliconflow.cn/v1/chat/completions", 
                      json=payload, 
                      headers={"Authorization": f"Bearer {key}"})
    
    res = r.json()['choices'][0]['message']['content']
    print("\n--- 🌟 真正的人工智能汉化文本 🌟 ---")
    print(res)

if __name__ == "__main__":
    get_real_translation()

# -*- coding: utf-8 -*-
import json, os, requests

def debug_translation():
    # 读取密钥
    with open(r"C:\Users\Administrator\Desktop\HorrorAgent_Project\.env", "r") as f:
        api_key = [line for line in f if "SILICONFLOW_API_KEY" in line][0].split("=")[1].strip().split()[0]
    
    url = "https://api.siliconflow.cn/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    # 模拟我们要翻译的一小段内容
    payload = {
        "model": "deepseek-ai/DeepSeek-V3",
        "messages": [{"role": "user", "content": "请将这段英文翻译成中文 JSON 数组: [{'id': 0, 'text': 'Hello world'}]，格式要求：[{'index': 0, 'zh': '...'}]"}],
        "temperature": 0
    }
    
    resp = requests.post(url, json=payload, timeout=60).json()
    raw_content = resp['choices'][0]['message']['content']
    print("--- RAW LLM OUTPUT ---")
    print(raw_content)
    print("--- END ---")

if __name__ == "__main__":
    debug_translation()

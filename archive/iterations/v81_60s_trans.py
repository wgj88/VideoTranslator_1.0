# -*- coding: utf-8 -*-
import json, requests, os, re

def run_v81_translation():
    input_p = r"E:\VideoTranslator_Project\unhinged_tech\RAW_EN_SCRIPT.json"
    dotenv_p = r"C:\Users\Administrator\Desktop\HorrorAgent_Project\.env"
    with open(dotenv_p, "r") as f:
        api_key = [l for l in f if "SILICONFLOW_API_KEY" in l][0].split("=")[1].strip().split()[0].replace('"', '').replace("'", "")
    
    with open(input_p, "r", encoding="utf-8") as f: data = json.load(f)
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    # 截取前 60s
    test_batch = [it for it in data if it['start'] < 60]
    print(f"\n--- ✍️ 正在铸造 V81 【标点换气版】前一分钟剧本 ---")

    for i, item in enumerate(test_batch):
        dur = item['end'] - item['start']
        max_chars = int((dur - 0.2) * 5.06)
        
        prompt = f"你是一个配音导演。请将这段话转为‘舒缓脱水版’中文字幕。要求：1.字数严控在 {max_chars} 内。2.必须正确使用标点（，。！？）物理引导AI停顿。3.数字汉化。4.句号结尾。原文：{item['text']}。直接返回JSON:{{'zh': '...'}}"
        
        try:
            r = requests.post("https://api.siliconflow.cn/v1/chat/completions", json={
                "model": "deepseek-ai/DeepSeek-V3", "messages": [{"role": "user", "content": prompt}], "temperature": 0.2
            }, headers=headers).json()
            zh = json.loads(re.search(r"\{.*\}", r['choices'][0]['message']['content'], re.DOTALL).group())['zh']
            print(f"  -> [{i+1}] {zh}")
            item['zh'] = zh
        except: pass

    with open(r"E:\VideoTranslator_Project\unhinged_tech\V81_60S_SCRIPT.json", "w", encoding="utf-8") as f:
        json.dump(test_batch, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    run_v81_translation()

# -*- coding: utf-8 -*-
import json, requests, os, re

def run_punc_refine():
    input_p = r"E:\VideoTranslator_Project\unhinged_tech\RAW_EN_SCRIPT.json"
    dotenv_p = r"C:\Users\Administrator\Desktop\HorrorAgent_Project\.env"
    with open(dotenv_p, "r") as f:
        api_key = [l for l in f if "SILICONFLOW_API_KEY" in l][0].split("=")[1].strip().split()[0].replace('"', '').replace("'", "")
    
    with open(input_p, "r", encoding="utf-8") as f: data = json.load(f)
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    print("\n--- ✍️ 正在执行 V81 【呼吸感补完】剧本重塑 ---")

    for i in range(10): # 先对前10句执行示范
        item = data[i]
        dur = item['end'] - item['start']
        max_chars = int((dur - 0.2) * 5.06)
        
        prompt = f"""你是一个专业的视频配音导演。请将这段话转为‘舒缓脱水版’中文字幕。
【规则】
1. 字数控制在 {max_chars} 个汉字以内（不含标点）。
2. 必须正确使用标点符号（，。！？：），用于引导 AI 的停顿和语气。
3. 语气利落、地道，数字全汉化。
4. 句号结尾。

原文：{item['text']}
直接返回 JSON: {{"zh": "..."}}
"""
        try:
            r = requests.post("https://api.siliconflow.cn/v1/chat/completions", json={
                "model": "deepseek-ai/DeepSeek-V3",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2
            }, headers=headers, timeout=20).json()
            
            zh = json.loads(re.search(r"\{.*\}", r['choices'][0]['message']['content'], re.DOTALL).group())['zh']
            print(f"  -> [{i+1}] 优化后: {zh}")
            item['zh'] = zh
        except: pass

    with open(r"E:\VideoTranslator_Project\unhinged_tech\V81_PUNC_SCRIPT.json", "w", encoding="utf-8") as f:
        json.dump(data[:10], f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    run_punc_refine()

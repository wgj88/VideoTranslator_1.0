# -*- coding: utf-8 -*-
import json, requests, os, re

def refine_formal():
    input_p = r"E:\VideoTranslator_Project\unhinged_tech\UNHINGED_FINAL_506_SCRIPT.json"
    dotenv_p = r"C:\Users\Administrator\Desktop\HorrorAgent_Project\.env"
    with open(dotenv_p, "r") as f:
        api_key = [l for l in f if "SILICONFLOW_API_KEY" in l][0].split("=")[1].strip().split()[0].replace('"', '').replace("'", "")
    
    with open(input_p, "r", encoding="utf-8") as f: data = json.load(f)
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    print("\n--- 🎙️ 正在执行【播音员级】全汉化正规化 ---")

    for i in range(5):
        text = data[i]['zh']
        prompt = f"你是一个专业播音员。请将这段话转为‘全中文书面语’。要求：1. 数字写成汉字（如三千五）。2. 英文缩写写成中文（如人工智能、图形处理器）。3. 禁止任何网络黑话。4. 在长句处保留 [pause]。原文：{text}。直接返回JSON:{{'zh': '...'}}"
        
        try:
            r = requests.post("https://api.siliconflow.cn/v1/chat/completions", json={
                "model": "deepseek-ai/DeepSeek-V3",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1
            }, headers=headers).json()
            
            zh = json.loads(re.search(r"\{.*\}", r['choices'][0]['message']['content'], re.DOTALL).group())['zh']
            print(f"  -> [{i+1}] 修正后: {zh}")
            data[i]['zh'] = zh
        except: pass

    with open(r"E:\VideoTranslator_Project\unhinged_tech\V70_FORMAL_SCRIPT.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    refine_formal()

# -*- coding: utf-8 -*-
import json, requests, os, re

def run_empathic_translation():
    # 1. 读取声学简报
    with open(r"E:\VideoTranslator_Project\unhinged_tech\V82_VIBE_REPORT.json", "r", encoding="utf-8") as f: vibes = json.load(f)
    
    dotenv_p = r"C:\Users\Administrator\Desktop\HorrorAgent_Project\.env"
    with open(dotenv_p, "r") as f:
        api_key = [l for l in f if "SILICONFLOW_API_KEY" in l][0].split("=")[1].strip().strip("'").strip('"').split()[0]

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    print("\n--- 🎭 启动 V82 【共情导演模式】：正在根据原片声谱重塑剧本 ---")

    refined_script = []
    for item in vibes:
        prompt = f"""你是一个顶级配音导演。我通过物理扫描探测到了原片博主的发音特征：
【本段声学指纹】
- 语速性格：{item['vibe']}
- 原始英文："{item['en_text']}"

【任务】
请将台词译为地道中文，并精准注入以下“演技标签”：
1. 若为‘深沉/延长’：大幅减少汉字数量，关键处使用‘——’拉长音，字里行间要有‘末世废土感’。
2. 若为‘急促吐槽’：字数稍多，用短促的标点。
3. 必须包含标点，返回 JSON: {{"zh": "..."}}

不要任何废话，直接给 JSON。
"""
        try:
            r = requests.post("https://api.siliconflow.cn/v1/chat/completions", json={
                "model": "deepseek-ai/DeepSeek-V3", "messages": [{"role": "user", "content": prompt}], "temperature": 0.5
            }, headers=headers, timeout=20).json()
            
            zh = json.loads(re.search(r"\{.*\}", r['choices'][0]['message']['content'], re.DOTALL).group())['zh']
            print(f"  -> [{item['id']}] Vibe:{item['vibe']} \n     剧本: {zh}")
            refined_script.append({"id": item['id'], "zh": zh})
        except: pass

    with open(r"E:\VideoTranslator_Project\unhinged_tech\V82_EMPATHY_SCRIPT.json", "w", encoding="utf-8") as f:
        json.dump(refined_script, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    run_empathic_translation()

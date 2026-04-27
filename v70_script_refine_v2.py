# -*- coding: utf-8 -*-
import json, requests, os, re

def clean_json(text):
    # 物理清除 Markdown 标签
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```\s*", "", text)
    return text.strip()

def refine_for_voxcpm_v2():
    input_p = r"E:\VideoTranslator_Project\unhinged_tech\UNHINGED_FINAL_506_SCRIPT.json"
    dotenv_p = r"C:\Users\Administrator\Desktop\HorrorAgent_Project\.env"
    with open(dotenv_p, "r") as f:
        api_key = [l for l in f if "SILICONFLOW_API_KEY" in l][0].split("=")[1].strip().split()[0].replace('"', '').replace("'", "")
    
    with open(input_p, "r", encoding="utf-8") as f: data = json.load(f)
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    print("\n--- ✍️ 正在执行【VoxCPM 亲和力】重塑 (带格式清洗) ---")

    for i in range(5):
        text = data[i]['zh']
        prompt = f"请将这段中文台词重写为AI配音亲和格式（数字汉化、缩写汉化、长句中间加 [pause]）。保持约 {len(text)} 字。原文：{text}。直接返回JSON:{{'refined_zh': '...'}}"
        
        try:
            r = requests.post("https://api.siliconflow.cn/v1/chat/completions", json={
                "model": "deepseek-ai/DeepSeek-V3",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1
            }, headers=headers).json()
            
            raw_content = r['choices'][0]['message']['content']
            content = json.loads(clean_json(raw_content))
            refined = content['refined_zh']
            print(f"  -> [{i+1}] 之前: {text}")
            print(f"     之后: {refined}")
            data[i]['zh'] = refined
        except Exception as e:
            print(f"  ⚠️ 处理 {i} 失败: {e}")

    with open(r"E:\VideoTranslator_Project\unhinged_tech\V70_REFINED_SCRIPT.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    refine_for_voxcpm_v2()

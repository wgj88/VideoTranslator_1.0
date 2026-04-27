# -*- coding: utf-8 -*-
import json, os, requests, re

def run_natural_translation():
    input_p = r"E:\VideoTranslator_Project\unhinged_tech\RAW_EN_SCRIPT.json"
    dotenv_p = r"C:\Users\Administrator\Desktop\HorrorAgent_Project\.env"
    with open(dotenv_p, "r") as f:
        api_key = [l for l in f if "SILICONFLOW_API_KEY" in l][0].split("=")[1].strip().split()[0].replace('"', '').replace("'", "")
    
    with open(input_p, "r", encoding="utf-8") as f: full_data = json.load(f)
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    final_natural_script = []
    print(f"\n[V68-Director] 正在执行“灵魂解封”翻译 (前 10 句)...")

    for i, item in enumerate(full_data[:10]):
        dur = item['end'] - item['start']
        # 给出字数上限，但不设下限
        max_len = int(dur * 5.5) 
        
        prompt = f"""你是一个顶级的B站科技区Up主。
【任务】请翻译这段英文台词。
【风格】极其地道、顺滑、有梗。要像真人在解说，不要翻译腔。
【空间限制】这一段最多只能容纳 {max_len} 个汉字。你可以写得短，但绝不能超过。
原文：{item['text']}
返回 JSON: {{"zh": "..."}}
"""
        try:
            r = requests.post("https://api.siliconflow.cn/v1/chat/completions", json={
                "model": "deepseek-ai/DeepSeek-V3",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3, "response_format": {"type": "json_object"}
            }, headers=headers, timeout=15).json()
            zh = json.loads(r['choices'][0]['message']['content'])['zh']
            item['zh'] = zh
            final_natural_script.append(item)
            print(f"  -> [{i+1}] 空间:{dur:.1f}s | 译文: {zh}")
        except:
            print(f"  ⚠️ 片段 {i} 失败")

    with open(r"E:\VideoTranslator_Project\unhinged_tech\V68_NATURAL_SCRIPT.json", "w", encoding="utf-8") as f:
        json.dump(final_natural_script, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    run_natural_translation()

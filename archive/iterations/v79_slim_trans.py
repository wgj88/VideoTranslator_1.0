# -*- coding: utf-8 -*-
import json, requests, os, re

def run_slim_translation():
    input_p = r"E:\VideoTranslator_Project\unhinged_tech\RAW_EN_SCRIPT.json"
    dotenv_p = r"C:\Users\Administrator\Desktop\HorrorAgent_Project\.env"
    with open(dotenv_p, "r") as f:
        api_key = [l for l in f if "SILICONFLOW_API_KEY" in l][0].split("=")[1].strip().split()[0].replace('"', '').replace("'", "")
    
    with open(input_p, "r", encoding="utf-8") as f: data = json.load(f)
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    CPS_TARGET = 5.06
    print(f"\n--- 🧪 正在执行 V79 【脱水灵魂版】重译 (目标 CPS: {CPS_TARGET}) ---")

    test_batch = data[:10]
    for i, item in enumerate(test_batch):
        dur = item['end'] - item['start']
        # 计算严格字数上限（向下取整，留出 0.2s 呼吸余量）
        max_chars = int((dur - 0.2) * CPS_TARGET)
        
        prompt = f"""你是一个B站硬核科技博主。请将这段话转为地道中文字幕。
【地狱级约束】
1. 字数绝对严禁超过 {max_chars} 个汉字（当前时长 {dur:.1f}s）。
2. 语气要极其利落，像真人随口吐槽，拒绝翻译腔。
3. 数字/英文全汉化。

原文：{item['text']}
直接返回 JSON: {{"zh": "..."}}
"""
        try:
            r = requests.post("https://api.siliconflow.cn/v1/chat/completions", json={
                "model": "deepseek-ai/DeepSeek-V3",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3
            }, headers=headers, timeout=20).json()
            
            content = r['choices'][0]['message']['content']
            zh = json.loads(re.search(r"\{.*\}", content, re.DOTALL).group())['zh']
            
            real_cps = len(zh) / dur
            print(f"  -> [{i+1}] 长度:{len(zh)}/{max_chars} | CPS:{real_cps:.2f} | 译文: {zh}")
            item['zh'] = zh
        except: pass

    with open(r"E:\VideoTranslator_Project\unhinged_tech\V79_SLIM_SCRIPT.json", "w", encoding="utf-8") as f:
        json.dump(test_batch, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    run_slim_translation()

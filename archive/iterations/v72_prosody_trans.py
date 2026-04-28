# -*- coding: utf-8 -*-
import json, requests, os, re

def run_prosodic_translation():
    input_p = r"E:\VideoTranslator_Project\unhinged_tech\RAW_EN_SCRIPT.json"
    dotenv_p = r"C:\Users\Administrator\Desktop\HorrorAgent_Project\.env"
    with open(dotenv_p, "r") as f:
        api_key = [l for l in f if "SILICONFLOW_API_KEY" in l][0].split("=")[1].strip().split()[0].replace('"', '').replace("'", "")
    
    with open(input_p, "r", encoding="utf-8") as f: data = json.load(f)
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    print("\n--- 🎭 正在执行【韵律导演级】地道汉化 (拒绝凑字数) ---")

    for i in range(10):
        item = data[i]
        dur = item['end'] - item['start']
        
        # 给出时长限制，但不给硬性字数配额，只给参考范围
        prompt = f"""你是一个顶级的B站科技博主。请将这段台词进行“灵魂级汉化”。
【核心原则】
1. 拒绝拗口：必须符合中文母语者的语言习惯，利落、干练。
2. 语义对齐：保留原片的“讽刺”和“硬核”调性，宁可神似，不要形似。
3. 时空参考：这段话在视频里大约有 {dur:.1f} 秒的时间窗口。
   - 如果原文很短，你可以留白，不用非得填满。
   - 如果原文很长，请提炼金句，不要读成绕口令。
4. 正典化：数字写成汉字。

原文：{item['text']}
直接返回 JSON: {{"zh": "..."}}
"""
        try:
            r = requests.post("https://api.siliconflow.cn/v1/chat/completions", json={
                "model": "deepseek-ai/DeepSeek-V3",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3
            }, headers=headers, timeout=20).json()
            
            zh = json.loads(re.search(r"\{.*\}", r['choices'][0]['message']['content'], re.DOTALL).group())['zh']
            print(f"  -> [{i+1}] 英文: {item['text'][:30]}...")
            print(f"     地道中文: {zh} (耗时窗:{dur:.1f}s)")
            item['zh'] = zh
        except: pass

    with open(r"E:\VideoTranslator_Project\unhinged_tech\V72_PROSODY_SCRIPT.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    run_prosodic_translation()

# -*- coding: utf-8 -*-
import json, requests, os, re

def run_blackwell_translation():
    print("\n--- ✍️ 正在铸造【项目2】首批灵魂剧本 ---")
    
    # 模拟原始英文时间轴 (基于 v86 侦察结果)
    raw_en = [
        {"id": 1, "start": 0.0, "end": 4.5, "text": "The wait is finally over. Blackwell is here and it's absolute monster."},
        {"id": 2, "start": 4.5, "end": 8.2, "text": "We are talking about 200 teraflops of pure computing power in your palm."},
        {"id": 3, "start": 8.2, "end": 12.5, "text": "But at what cost? $4,000 for a GPU? Nvidia has officially lost its mind."},
        {"id": 4, "start": 12.5, "end": 15.8, "text": "Yet, every single AI lab on the planet is lining up to buy them."},
        {"id": 5, "start": 15.8, "end": 19.5, "text": "Is it the future of AI or just the biggest wealth transfer in history?"}
    ]

    dotenv_p = r"C:\Users\Administrator\Desktop\HorrorAgent_Project\.env"
    with open(dotenv_p, "r") as f:
        api_key = [l for l in f if "SILICONFLOW_API_KEY" in l][0].split("=")[1].strip().strip("'").strip('"').split()[0]
    
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    CPS = 4.5
    final_script = []

    for item in raw_en:
        dur = item['end'] - item['start']
        max_chars = int((dur - 0.2) * CPS)
        
        prompt = f"""你是一个硬核科技区博主。请将这段话转为播音员级剧本。
【地狱约束】
1. 字数必须严控在 {max_chars} 个汉字内。
2. 必须包含标点（，。！？）。
3. 数字、单位、全称必须全汉化（如 $4,000 转为“四千美元”）。
4. 语气要酷，不要翻译腔。

原文：{item['text']}
返回 JSON: {{"zh": "..."}}
"""
        try:
            r = requests.post("https://api.siliconflow.cn/v1/chat/completions", json={
                "model": "deepseek-ai/DeepSeek-V3", "messages": [{"role": "user", "content": prompt}], "temperature": 0.2
            }, headers=headers, timeout=20).json()
            
            zh = json.loads(re.search(r"\{.*\}", r['choices'][0]['message']['content'], re.DOTALL).group())['zh']
            print(f"  ✅ [{item['id']}] {zh}")
            item['zh'] = zh
            final_script.append(item)
        except: pass

    with open(r"E:\VideoTranslator_Project\blackwell_vlog\scripts\V87_PROSODY_SCRIPT.json", "w", encoding="utf-8") as f:
        json.dump(final_script, f, ensure_ascii=False, indent=2)
    print("\n🏁 Blackwell 首批剧本铸造完成。")

if __name__ == "__main__":
    run_blackwell_translation()

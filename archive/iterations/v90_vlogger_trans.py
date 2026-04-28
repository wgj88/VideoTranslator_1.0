# -*- coding: utf-8 -*-
import json, requests, os, re

def run_v90_vlogger_trans():
    print("\n--- 🎤 正在启动 V90 【博主重塑计划】：让 AI 说人话 ---")
    
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
    final_script = []

    for item in raw_en:
        dur = item['end'] - item['start']
        max_chars = int((dur - 0.2) * 4.5)
        
        prompt = f"""你是一个B站百万粉丝的硬核数码UP主（参考何同学或极客湾风格）。
【任务】
请将这段台词转为极其地道的‘人话’。
1. 严禁使用“久候终至”、“代价几何”这类书面词。
2. 语气要像在镜头前随口聊天，带点兴奋和吐槽感。
3. 必须符合 {max_chars} 个汉字的字数限制。
4. 英文术语、数字全汉化（GPU->显卡，$4000->四千美元）。

原文：{item['text']}
返回 JSON: {{"zh": "..."}}
"""
        try:
            r = requests.post("https://api.siliconflow.cn/v1/chat/completions", json={
                "model": "deepseek-ai/DeepSeek-V3", "messages": [{"role": "user", "content": prompt}], "temperature": 0.7
            }, headers=headers, timeout=20).json()
            
            zh = json.loads(re.search(r"\{.*\}", r['choices'][0]['message']['content'], re.DOTALL).group())['zh']
            print(f"  -> [{item['id']}] {zh}")
            item['zh'] = zh
            final_script.append(item)
        except: pass

    with open(r"E:\VideoTranslator_Project\blackwell_vlog\scripts\V90_VLOGGER_SCRIPT.json", "w", encoding="utf-8") as f:
        json.dump(final_script, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    run_v90_vlogger_trans()

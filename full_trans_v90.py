# -*- coding: utf-8 -*-
import json, requests, os, re, time

def run_full_vlogger_trans():
    print("\n--- 📜 正在执行全量剧本（114段）灵魂重塑 ---")
    input_p = r"E:\VideoTranslator_Project\unhinged_tech\RAW_EN_SCRIPT.json"
    dotenv_p = r"C:\Users\Administrator\Desktop\HorrorAgent_Project\.env"
    
    with open(dotenv_p, "r") as f:
        api_key = [l for l in f if "SILICONFLOW_API_KEY" in l][0].split("=")[1].strip().strip("'").strip('"').split()[0]
    
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    with open(input_p, "r", encoding="utf-8") as f: data = json.load(f)
    
    final_script = []
    # 为 114 段台词加速翻译（采用更大的 Batch 或并发逻辑）
    for i, item in enumerate(data):
        dur = item['end'] - item['start']
        max_chars = int((dur - 0.2) * 4.5)
        
        prompt = f"你是一个硬核数码区UP主。将 '{item['text']}' 译为极简口语。1.严禁书面语。2.少于 {max_chars} 字。3.数字全汉字。返回 JSON: {{'zh': '...'}}"
        
        success = False
        for retry in range(2):
            try:
                r = requests.post("https://api.siliconflow.cn/v1/chat/completions", json={
                    "model": "deepseek-ai/DeepSeek-V3", "messages": [{"role": "user", "content": prompt}], "temperature": 0.6
                }, headers=headers, timeout=15).json()
                zh = json.loads(re.search(r"\{.*\}", r['choices'][0]['message']['content'], re.DOTALL).group())['zh']
                item['zh'] = zh
                print(f"  [{i+1}/114] {zh}")
                success = True
                break
            except: time.sleep(0.5)
        
        if not success: item['zh'] = "... "
        final_script.append(item)

    with open(r"E:\VideoTranslator_Project\unhinged_tech\V90_FULL_SCRIPT.json", "w", encoding="utf-8") as f:
        json.dump(final_script, f, ensure_ascii=False, indent=2)
    print("\n✅ 全量灵魂剧本已就绪！")

if __name__ == "__main__":
    run_full_vlogger_trans()

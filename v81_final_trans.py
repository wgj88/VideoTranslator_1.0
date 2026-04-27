# -*- coding: utf-8 -*-
import json, requests, os, re, time

def run_v81_ultra_stable():
    print("🔥 正在执行 V81 剧本全量导演（高容错版）...")
    input_p = r"E:\VideoTranslator_Project\unhinged_tech\RAW_EN_SCRIPT.json"
    dotenv_p = r"C:\Users\Administrator\Desktop\HorrorAgent_Project\.env"
    
    with open(dotenv_p, "r") as f:
        api_key = [l for l in f if "SILICONFLOW_API_KEY" in l][0].split("=")[1].strip().strip("'").strip('"').split()[0]

    with open(input_p, "r", encoding="utf-8") as f: data = json.load(f)
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    test_batch = [it for it in data if it['start'] < 60]
    final_script = []

    for i, item in enumerate(test_batch):
        dur = item['end'] - item['start']
        max_chars = int((dur - 0.3) * 4.5)
        
        prompt = f"你是一个科技解说。将 '{item['text']}' 译为地道中文，少于 {max_chars} 字，必须带标点。返回 JSON 格式: {{\"zh\": \"...\"}}，不要包含任何其他文字。"
        
        success = False
        for retry in range(3):
            try:
                r = requests.post("https://api.siliconflow.cn/v1/chat/completions", json={
                    "model": "deepseek-ai/DeepSeek-V3", "messages": [{"role": "user", "content": prompt}], "temperature": 0.1
                }, headers=headers, timeout=15).json()
                
                raw_res = r['choices'][0]['message']['content']
                # 暴力清理
                match = re.search(r"\{.*\}", raw_res, re.DOTALL)
                if match:
                    zh = json.loads(match.group())['zh']
                    print(f"  ✅ [{i+1}/13] {zh}")
                    item['zh'] = zh
                    success = True
                    break
            except:
                time.sleep(1)
        
        if not success:
            print(f"  ⚠️ [{i+1}/13] 降级处理")
            item['zh'] = "。 " # 留空防崩
        final_script.append(item)

    with open(r"E:\VideoTranslator_Project\unhinged_tech\V81_60S_FIXED.json", "w", encoding="utf-8") as f:
        json.dump(final_script, f, ensure_ascii=False, indent=2)
    print("\n🏁 剧本导演工作完成。")

if __name__ == "__main__":
    run_v81_ultra_stable()

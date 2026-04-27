# -*- coding: utf-8 -*-
import json, os, requests, time

def run_2min_translation():
    input_p = r"E:\VideoTranslator_Project\unhinged_tech\RAW_EN_SCRIPT.json"
    dotenv_p = r"C:\Users\Administrator\Desktop\HorrorAgent_Project\.env"
    with open(dotenv_p, "r") as f:
        api_key = [l for l in f if "SILICONFLOW_API_KEY" in l][0].split("=")[1].strip().split()[0].replace('"', '').replace("'", "")
    
    with open(input_p, "r", encoding="utf-8") as f: data = json.load(f)
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    # 物理资产配置
    CPS = 5.06
    # 截取前 120 秒
    test_batch = [item for item in data if item['start'] < 120]
    final_script = []
    
    print(f"\n[Translator] 正在为前 2 分钟（共 {len(test_batch)} 段）设计“对齐版”台词...")

    for i, item in enumerate(test_batch):
        dur = item['end'] - item['start']
        target_len = max(4, int(dur * CPS))
        
        prompt = f"你是一个导演。请将 '{item['text']}' 翻译成约 {target_len} 个汉字。要求：必须填满时间轴，不留空白。返回 JSON: {{'zh': '...'}}"
        
        success = False
        for retry in range(3):
            try:
                r = requests.post("https://api.siliconflow.cn/v1/chat/completions", json={
                    "model": "deepseek-ai/DeepSeek-V3",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1, "response_format": {"type": "json_object"}
                }, headers=headers, timeout=15).json()
                zh = json.loads(r['choices'][0]['message']['content'])['zh']
                item['zh'] = zh
                final_script.append(item)
                print(f"  -> [{i+1}/{len(test_batch)}] 对齐成功: {zh}")
                success = True
                break
            except: time.sleep(0.5)
        
        if not success: final_script.append(item)

    with open(r"E:\VideoTranslator_Project\unhinged_tech\V69_2MIN_SCRIPT.json", "w", encoding="utf-8") as f:
        json.dump(final_script, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    run_2min_translation()

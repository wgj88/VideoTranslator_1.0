# -*- coding: utf-8 -*-
import json, os, requests, time

def run_balanced_translation():
    input_p = r"E:\VideoTranslator_Project\unhinged_tech\RAW_EN_SCRIPT.json"
    dotenv_p = r"C:\Users\Administrator\Desktop\HorrorAgent_Project\.env"
    with open(dotenv_p, "r") as f:
        api_key = [l for l in f if "SILICONFLOW_API_KEY" in l][0].split("=")[1].strip().split()[0].replace('"', '').replace("'", "")
    
    with open(input_p, "r", encoding="utf-8") as f: full_data = json.load(f)
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    test_batch = [item for item in full_data if item['start'] < 120.0]
    final_script = []
    # 科学语速常数
    CPS = 5.06

    print(f"\n[V77-Balanced] 正在执行黄金比例重译 (前 2 分钟)...")

    for i, item in enumerate(test_batch):
        dur = item['end'] - item['start']
        target_len = int(dur * CPS)
        
        prompt = f"你是个导演。请将 '{item['text']}' 翻译成约 {target_len} 个汉字的中文。要求：不要废话，要利落，字数必须物理匹配 {dur:.1f}s 的时长。返回JSON:{{'zh': '...'}}"
        
        for retry in range(5):
            try:
                r = requests.post("https://api.siliconflow.cn/v1/chat/completions", json={
                    "model": "deepseek-ai/DeepSeek-V3",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1, "response_format": {"type": "json_object"}
                }, headers=headers, timeout=15).json()
                zh = json.loads(r['choices'][0]['message']['content'])['zh']
                item['zh'] = zh
                final_script.append(item)
                print(f"  -> [{i+1}] 空间:{dur:.1f}s | 产出:{len(zh)}字: {zh}")
                break
            except: time.sleep(1)

    with open(r"E:\VideoTranslator_Project\unhinged_tech\V77_BALANCED_SCRIPT.json", "w", encoding="utf-8") as f:
        json.dump(final_script, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    run_balanced_translation()

# -*- coding: utf-8 -*-
import json, os, requests, time

def run_elastic_retry():
    input_p = r"E:\VideoTranslator_Project\unhinged_tech\RAW_EN_SCRIPT.json"
    dotenv_p = r"C:\Users\Administrator\Desktop\HorrorAgent_Project\.env"
    with open(dotenv_p, "r") as f:
        api_key = [l for l in f if "SILICONFLOW_API_KEY" in l][0].split("=")[1].strip().split()[0].replace('"', '').replace("'", "")
    
    with open(input_p, "r", encoding="utf-8") as f: full_data = json.load(f)
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    final_script = []
    print(f"\n[V69-Retry] 正在强行填满前 5 段台词...")

    for i, item in enumerate(full_data[:5]):
        dur = item['end'] - item['start']
        target_len = int(dur * 5.06)
        
        # 核心指令：要求它补齐字数
        prompt = f"你是一个导演。英文台词是 '{item['text']}'。这段有 {dur:.1f} 秒。为了填满时间轴且不显急促，请写出精准约 {target_len} 个汉字的中文翻译。你可以增加修饰词。返回JSON:{{'zh': '...'}}"
        
        for retry in range(10): # 死磕模式
            try:
                r = requests.post("https://api.siliconflow.cn/v1/chat/completions", json={
                    "model": "deepseek-ai/DeepSeek-V3",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3, "response_format": {"type": "json_object"}
                }, headers=headers, timeout=20).json()
                zh = json.loads(r['choices'][0]['message']['content'])['zh']
                item['zh'] = zh
                item['target_len'] = target_len
                final_script.append(item)
                print(f"  -> [{i+1}] 空间:{dur:.1f}s | 产出:{len(zh)}字: {zh}")
                break
            except:
                time.sleep(1)

    with open(r"E:\VideoTranslator_Project\unhinged_tech\V69_ELASTIC_SCRIPT.json", "w", encoding="utf-8") as f:
        json.dump(final_script, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    run_elastic_retry()

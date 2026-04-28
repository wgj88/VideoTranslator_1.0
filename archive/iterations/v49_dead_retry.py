# -*- coding: utf-8 -*-
import json, os, requests, time

def run_dead_retry():
    input_p = r"E:\VideoTranslator_Project\separated_audio\v9_final_script.json"
    dotenv_p = r"C:\Users\Administrator\Desktop\HorrorAgent_Project\.env"
    with open(dotenv_p, "r") as f:
        api_key = [l for l in f if "SILICONFLOW_API_KEY" in l][0].split("=")[1].strip().split()[0].replace('"', '').replace("'", "")

    with open(input_p, "r", encoding="utf-8") as f: data = json.load(f)
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    final_script = []
    print(f"\n[V49-Retry] 正在强力补全剧本...")

    for i, item in enumerate(data):
        dur = item['end'] - item['start']
        target_len = max(4, int(dur * 4.2))
        
        prompt = f"你是一个导演。请将 '{item['text']}' 翻译成约 {target_len} 个汉字的利落中文。返回格式:{{'zh': '...'}}"
        
        success = False
        for retry in range(5): # 死磕 5 次
            try:
                r = requests.post("https://api.siliconflow.cn/v1/chat/completions", json={
                    "model": "deepseek-ai/DeepSeek-V3",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1, "response_format": {"type": "json_object"}
                }, headers=headers, timeout=15).json()
                zh = json.loads(r['choices'][0]['message']['content'])['zh']
                item['zh'] = zh
                final_script.append(item)
                print(f"  -> [{i+1}/19] 成功: {zh}")
                success = True
                break
            except:
                time.sleep(1)
        
        if not success:
            print(f"  ⚠️ 片段 {i} 最终失败，跳过。")

    with open(r"E:\VideoTranslator_Project\separated_audio\V49_METRONOME_SCRIPT.json", "w", encoding="utf-8") as f:
        json.dump(final_script, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    run_dead_retry()

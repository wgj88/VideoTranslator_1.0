# -*- coding: utf-8 -*-
import json, os, requests, time

def run_unhinged_batch_translation(start_idx, end_idx, out_file):
    input_p = r"E:\VideoTranslator_Project\unhinged_tech\RAW_EN_SCRIPT.json"
    dotenv_p = r"C:\Users\Administrator\Desktop\HorrorAgent_Project\.env"
    with open(dotenv_p, "r") as f:
        api_key = [l for l in f if "SILICONFLOW_API_KEY" in l][0].split("=")[1].strip().split()[0].replace('"', '').replace("'", "")
    
    with open(input_p, "r", encoding="utf-8") as f: full_data = json.load(f)
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    batch = full_data[start_idx:end_idx]
    final_batch = []
    
    # 核心常数：定标语速 5.06
    CPS = 5.06

    print(f"\n[Translator] 正在处理第 {start_idx} 到 {end_idx} 句...")

    for i, item in enumerate(batch):
        dur = item['end'] - item['start']
        target_len = max(4, int(dur * CPS))
        
        prompt = f"""你是一个硬核科技解说员。
任务：翻译台词。
物理时空：{dur:.2f}秒。
硬性要求：字数必须控制在约 {target_len} 个汉字（正负误差1字）。
风格：利落、冷峻、专业。以“。”结尾。
原文：{item['text']}
返回 JSON: {{"zh": "..."}}
"""
        success = False
        for retry in range(5):
            try:
                r = requests.post("https://api.siliconflow.cn/v1/chat/completions", json={
                    "model": "deepseek-ai/DeepSeek-V3",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1, "response_format": {"type": "json_object"}
                }, headers=headers, timeout=20).json()
                zh = json.loads(r['choices'][0]['message']['content'])['zh']
                item['zh'] = zh
                item['target_len'] = target_len
                final_batch.append(item)
                print(f"  -> [{start_idx+i+1}] 理想 {target_len} | 产出 {len(zh)}: {zh}")
                success = True
                break
            except:
                time.sleep(1)
        
        if not success:
            print(f"  ⚠️ 片段 {start_idx+i} 失败，使用基础翻译...")
            item['zh'] = "。 " # 留空占位

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(final_batch, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    run_unhinged_batch_translation(0, 40, r"E:\VideoTranslator_Project\unhinged_tech\UNHINGED_PART1.json")

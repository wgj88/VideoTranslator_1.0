# -*- coding: utf-8 -*-
import os, sys, json, requests, re, time

def run_stable_translation():
    input_json = r"E:\VideoTranslator_Project\separated_audio\v9_final_script.json"
    dotenv_path = r"C:\Users\Administrator\Desktop\HorrorAgent_Project\.env"
    
    with open(dotenv_path, "r") as f:
        api_key = [l for l in f if "SILICONFLOW_API_KEY" in l][0].split("=")[1].strip().split()[0].replace('"', '').replace("'", "")

    with open(input_json, "r", encoding="utf-8") as f: data = json.load(f)

    print(f"\n[V27-Stable] 正在通过 DeepSeek-V3 执行导演级汉化...")

    final_script = []
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    for i, item in enumerate(data):
        # 逐句重译，确保最高的稳定性
        prompt = f"""将这句视频台词翻译成地道、口语化的中文。
要求：
1. 像真人解说。增加“了、以及、正”等辅助词。
2. 严禁翻译腔。如果太长，请拆成两句。
3. 必须以“。”或“！”结尾。

英文台词：{item['text']}
返回格式：{{"zh": "..."}}
"""
        payload = {
            "model": "deepseek-ai/DeepSeek-V3",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "response_format": {"type": "json_object"}
        }

        max_retries = 3
        for retry in range(max_retries):
            try:
                r = requests.post("https://api.siliconflow.cn/v1/chat/completions", json=payload, headers=headers, timeout=20).json()
                content = json.loads(r['choices'][0]['message']['content'])
                zh_full = content['zh']
                
                # 语义切割逻辑
                sub_parts = re.split(r'([。！？；]+)', zh_full)
                clean_parts = []
                for k in range(0, len(sub_parts)-1, 2): clean_parts.append(sub_parts[k] + sub_parts[k+1])
                if len(sub_parts) % 2 == 1: clean_parts.append(sub_parts[-1])

                orig_dur = item['end'] - item['start']
                curr_t = item['start']
                for p in clean_parts:
                    p = p.strip()
                    if not p: continue
                    p_dur = (len(p) / len(zh_full)) * orig_dur
                    final_script.append({
                        "start": round(curr_t, 3), "end": round(curr_t + p_dur, 3),
                        "speaker": item.get('speaker', 'SPEAKER_00'), "zh": p
                    })
                    curr_t += p_dur
                print(f"  -> [{i+1}/{len(data)}] 完成: {zh_full[:20]}...")
                break
            except Exception as e:
                print(f"     ⚠️ 重试 {retry+1}/3: {e}")
                time.sleep(1)

    out_path = r"E:\VideoTranslator_Project\separated_audio\V27_ULTIMATE_SCRIPT.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(final_script, f, ensure_ascii=False, indent=2)
    print(f"\n🏆 全篇剧本重塑大功告成：{out_path}")

if __name__ == "__main__":
    run_stable_translation()

# -*- coding: utf-8 -*-
import json, os, requests, re

def run_calibrated_translation():
    input_p = r"E:\VideoTranslator_Project\separated_audio\v9_final_script.json"
    dotenv_p = r"C:\Users\Administrator\Desktop\HorrorAgent_Project\.env"
    with open(dotenv_p, "r") as f:
        api_key = [l for l in f if "SILICONFLOW_API_KEY" in l][0].split("=")[1].strip().split()[0].replace('"', '').replace("'", "")

    with open(input_p, "r", encoding="utf-8") as f: data = json.load(f)

    print(f"\n[V51-Precision] 正在执行【声速定标: 5.06 CPS】深度汉化...")

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    final_script = []

    for i, item in enumerate(data):
        dur = item['end'] - item['start']
        # 使用测定的 CPS: 5.06
        target_len = max(5, int(dur * 5.06))
        
        prompt = f"""你是一个顶级的配音导演。
【任务】翻译这段台词，字数必须物理适配视频时空。
【测定语速】本视频主讲人的中文语速为每秒 5.06 个汉字。
【物理时空】这一段在画面中占据 {dur:.2f} 秒。
【硬性指标】为了填满时轴且不留空白，你必须精准写出约 {target_len} 个汉字（绝对误差不超过2字）。

英文：{item['text']}
返回 JSON: {{"zh": "..."}}
"""
        payload = {
            "model": "deepseek-ai/DeepSeek-V3",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "response_format": {"type": "json_object"}
        }

        try:
            r = requests.post("https://api.siliconflow.cn/v1/chat/completions", json=payload, headers=headers, timeout=20).json()
            zh = json.loads(r['choices'][0]['message']['content'])['zh']
            item['zh'] = zh
            final_script.append(item)
            print(f"  -> [{i+1}/19] 时长 {dur:.1f}s | 理想字数 {target_len} | 产出 {len(zh)}: {zh}")
        except:
            print(f"  ⚠️ 片段 {i} 失败...")

    out_p = r"E:\VideoTranslator_Project\separated_audio\V51_CALIBRATED_SCRIPT.json"
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(final_script, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    run_calibrated_translation()

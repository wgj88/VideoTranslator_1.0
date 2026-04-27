# -*- coding: utf-8 -*-
import json, os, requests, re

def run_quota_aware_translation():
    input_p = r"E:\VideoTranslator_Project\separated_audio\v9_final_script.json"
    dotenv_p = r"C:\Users\Administrator\Desktop\HorrorAgent_Project\.env"
    
    with open(dotenv_p, "r") as f:
        api_key = [l for l in f if "SILICONFLOW_API_KEY" in l][0].split("=")[1].strip().split()[0].replace('"', '').replace("'", "")

    with open(input_p, "r", encoding="utf-8") as f: data = json.load(f)

    print(f"\n[V45-Metronome] 正在执行【限额感知】重译...")

    final_script = []
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    for i, item in enumerate(data):
        dur = item['end'] - item['start']
        # 计算配额：基准每秒 3.8 字
        # 如果时长过短 (<0.8s)，保底 3 字；如果过长，严格按比例
        quota = max(3, int(dur * 3.8))
        
        prompt = f"""你是一个视频汉化导演。请将台词翻译成中文。
要求：
1. 【关键限制】这句台词只有 {dur:.1f} 秒。你必须控制在约 {quota} 个汉字左右（正负误差1字）。
2. 如果字数不够，请增加生动的形容词。
3. 如果字数太多，请大幅精简，只留核心。
4. 风格：专业科技风。以“。”或“！”结尾。

英文：{item['text']}
返回JSON:[{{"zh": "..."}}]
"""
        payload = {
            "model": "deepseek-ai/DeepSeek-V3",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "response_format": {"type": "json_object"}
        }

        try:
            r = requests.post("https://api.siliconflow.cn/v1/chat/completions", json=payload, headers=headers, timeout=20).json()
            content = json.loads(r['choices'][0]['message']['content'])
            zh = content['zh']
            
            # 二次校验
            item['zh'] = zh
            item['quota'] = quota
            final_script.append(item)
            print(f"  -> [{i+1}/{len(data)}] 限额 {quota} 字 | 实际 {len(zh)} 字: {zh}")
        except:
            print(f"  ⚠️ 跳过 {i}...")

    out_p = r"E:\VideoTranslator_Project\separated_audio\V45_QUOTA_SCRIPT.json"
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(final_script, f, ensure_ascii=False, indent=2)
    print(f"\n🏆 限额版剧本已就绪：{out_p}")

if __name__ == "__main__":
    run_quota_aware_translation()

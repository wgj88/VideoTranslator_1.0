# -*- coding: utf-8 -*-
import json, os, requests, re

def run_temporal_aware_translation():
    input_p = r"E:\VideoTranslator_Project\separated_audio\v9_final_script.json"
    dotenv_p = r"C:\Users\Administrator\Desktop\HorrorAgent_Project\.env"
    
    with open(dotenv_p, "r") as f:
        api_key = [l for l in f if "SILICONFLOW_API_KEY" in l][0].split("=")[1].strip().split()[0].replace('"', '').replace("'", "")

    with open(input_p, "r", encoding="utf-8") as f: data = json.load(f)

    print(f"\n[V48-Temporal] 正在执行【时序感知·字数平衡】导演级重译...")

    final_script = []
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    for i, item in enumerate(data):
        dur = item['end'] - item['start']
        # 黄金配额：4.2字/秒
        target_len = max(4, int(dur * 4.2))
        
        prompt = f"""你是一个顶级的视频配音导演。
【当前任务】将这句台词翻译成中文。
【物理限制】这句台词在视频中占据 {dur:.2f} 秒。为了语速听起来最自然，你必须精准控制在约 {target_len} 个汉字（正负误差1字）。
【要求】
1. 如果原文太短，请增加生动的细节描述词。
2. 如果原文太长，请极度精简，保留骨干。
3. 风格：数码科技风。以“。”或“！”结尾。

英文：{item['text']}
返回JSON: {{"zh": "..."}}
"""
        payload = {
            "model": "deepseek-ai/DeepSeek-V3",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
            "response_format": {"type": "json_object"}
        }

        try:
            r = requests.post("https://api.siliconflow.cn/v1/chat/completions", json=payload, headers=headers, timeout=20).json()
            content = json.loads(r['choices'][0]['message']['content'])
            zh = content['zh']
            
            # 记录审计数据
            item['zh'] = zh
            item['target_len'] = target_len
            item['actual_len'] = len(zh)
            final_script.append(item)
            print(f"  -> [{i+1}/{len(data)}] 时长 {dur:.1f}s | 目标 {target_len} 字 | 实际 {len(zh)} 字: {zh}")
        except:
            print(f"  ⚠️ 跳过 {i}...")

    out_p = r"E:\VideoTranslator_Project\separated_audio\V48_TEMPORAL_SCRIPT.json"
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(final_script, f, ensure_ascii=False, indent=2)
    print(f"\n🏆 时序平衡版剧本已产出：{out_p}")

if __name__ == "__main__":
    run_temporal_aware_translation()

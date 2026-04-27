# -*- coding: utf-8 -*-
import json, os, requests, re

def run_elastic_translation():
    input_p = r"E:\VideoTranslator_Project\unhinged_tech\RAW_EN_SCRIPT.json"
    dotenv_p = r"C:\Users\Administrator\Desktop\HorrorAgent_Project\.env"
    with open(dotenv_p, "r") as f:
        api_key = [l for l in f if "SILICONFLOW_API_KEY" in l][0].split("=")[1].strip().split()[0].replace('"', '').replace("'", "")
    
    with open(input_p, "r", encoding="utf-8") as f: full_data = json.load(f)
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    final_elastic_script = []
    print(f"\n[V69-Elastic] 正在执行“弹性字数”自适应重译...")

    # 处理前 5 句作为演示
    for i, item in enumerate(full_data[:5]):
        dur = item['end'] - item['start']
        # 定标语速 5.06 字/秒
        target_len = int(dur * 5.06)
        
        prompt = f"""你是一个顶级的视频配音导演。
【当前任务】翻译这段台词，并精准控制语速节奏。
【物理时空】这一段在画面中占据 {dur:.2f} 秒。
【目标字数】为了语速最自然，你必须精准控制在约 {target_len} 个汉字左右（正负误差1字）。
【导演守则】
1. 如果原文翻译太短，请尽可能啰嗦一点，补充生动的细节描述词，把字数凑够。
2. 如果原文翻译太长，请极度精简，确保不顶破时间轴。
3. 风格：地道、带梗、Up主解说风。
原文：{item['text']}
返回 JSON: {{"zh": "..."}}
"""
        try:
            r = requests.post("https://api.siliconflow.cn/v1/chat/completions", json={
                "model": "deepseek-ai/DeepSeek-V3",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3, "response_format": {"type": "json_object"}
            }, headers=headers, timeout=15).json()
            zh = json.loads(r['choices'][0]['message']['content'])['zh']
            item['zh'] = zh
            item['target_len'] = target_len
            final_elastic_script.append(item)
            print(f"  -> [{i+1}] 空间:{dur:.1f}s | 理想字数:{target_len} | 产出字数:{len(zh)}: {zh}")
        except:
            print(f"  ⚠️ 片段 {i} 失败")

    with open(r"E:\VideoTranslator_Project\unhinged_tech\V69_ELASTIC_SCRIPT.json", "w", encoding="utf-8") as f:
        json.dump(final_elastic_script, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    run_elastic_translation()

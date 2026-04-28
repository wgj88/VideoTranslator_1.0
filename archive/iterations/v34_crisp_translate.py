# -*- coding: utf-8 -*-
import os, sys, json, requests, re

def run_crisp_translation():
    input_json = r"E:\VideoTranslator_Project\separated_audio\v9_final_script.json"
    dotenv_path = r"C:\Users\Administrator\Desktop\HorrorAgent_Project\.env"
    
    with open(dotenv_path, "r") as f:
        api_key = [l for l in f if "SILICONFLOW_API_KEY" in l][0].split("=")[1].strip().split()[0].replace('"', '').replace("'", "")

    with open(input_json, "r", encoding="utf-8") as f: data = json.load(f)

    print(f"\n[V34-Crisp] 正在执行【极简科技风】剧本脱水...")

    final_script = []
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    for i, item in enumerate(data):
        prompt = f"""将这句视频台词翻译成专业、利落的中文解说。
要求：
1. 风格：专业、数码博主风格。
2. 【核心限制】禁止在句末使用“了、吧、呢、啊、咯”等任何语气词！
3. 语言干练，严禁翻译腔。
4. 必须以“。”或“！”结尾。

英文台词：{item['text']}
返回格式：{{"zh": "..."}}
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
            zh_clean = content['zh']
            
            # 物理纠偏：防止 LLM 偷跑语气词
            zh_clean = re.sub(r'[了吧呢啊咯][。！]$', '。', zh_clean)

            final_script.append({
                "start": item['start'], "end": item['end'],
                "speaker": item.get('speaker', 'SPEAKER_00'), "zh": zh_clean
            })
            print(f"  -> [{i+1}/{len(data)}] 净化后: {zh_clean}")
        except:
            print(f"  ⚠️ 跳过一句...")

    out_path = r"E:\VideoTranslator_Project\separated_audio\V34_CRISP_SCRIPT.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(final_script, f, ensure_ascii=False, indent=2)
    print(f"\n🏆 极简版剧本已产出：{out_path}")

if __name__ == "__main__":
    run_crisp_translation()

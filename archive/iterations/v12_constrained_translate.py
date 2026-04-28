# -*- coding: utf-8 -*-
import os, sys, json, requests, re, time

def run_constrained_translation():
    input_json = r"E:\VideoTranslator_Project\separated_audio\v9_final_script.json"
    dotenv_path = r"C:\Users\Administrator\Desktop\HorrorAgent_Project\.env"
    
    with open(dotenv_path, "r") as f:
        api_key = [l for l in f if "SILICONFLOW_API_KEY" in l][0].split("=")[1].strip().replace('"', '').replace("'", "")

    with open(input_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"\n[Constraint-Trans] 正在执行【标点约束版】全篇汉化...")

    final_script = []
    
    batch_size = 10
    for i in range(0, len(data), batch_size):
        batch = data[i:i+batch_size]
        text_payload = "\n".join([f"ID_{j+i}: {item['text']}" for j, item in enumerate(batch)])
        
        # --- 核心改进：极其严苛的标点约束 Prompt ---
        prompt = f"""你是一个顶级的视频配音脚本主编。请将以下内容翻译成中文。
要求：
1. 【重要】每一句的末尾必须以“。”、“！”或“？”结束，严禁以“，”结束或不加标点。
2. 情感强烈的句子（如Wow, Look等）必须使用“！”。
3. 必须100%使用中文全角标点，严禁出现半角标点。
4. 语言要口语化，适合短视频解说风格。
5. 返回JSON数组格式：[{{"id": 数字, "zh": "..."}}]。

内容：
{text_payload}
"""
        payload = {
            "model": "deepseek-ai/DeepSeek-V3",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "response_format": {"type": "json_object"}
        }
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        
        try:
            r = requests.post("https://api.siliconflow.cn/v1/chat/completions", json=payload, headers=headers).json()
            content = r['choices'][0]['message']['content']
            match = re.search(r'\[.*\]', content, re.DOTALL)
            if match:
                trans_list = json.loads(match.group())
                for res in trans_list:
                    idx = int(res['id'])
                    # 语义二次切割逻辑保持
                    zh_full = res['zh']
                    sub_parts = re.split(r'([。！？；]+)', zh_full)
                    orig_start, orig_end = data[idx]['start'], data[idx]['end']
                    orig_dur = orig_end - orig_start
                    total_zh_len = len(zh_full)
                    curr_t = orig_start
                    
                    clean_parts = []
                    for k in range(0, len(sub_parts)-1, 2):
                        clean_parts.append(sub_parts[k] + sub_parts[k+1])
                    if len(sub_parts) % 2 == 1: clean_parts.append(sub_parts[-1])

                    for p in clean_parts:
                        p = p.strip()
                        if not p: continue
                        # 兜底检查：如果切分后还是没标点，强制补齐
                        if not p.endswith(('。','！','？')): p += "。"
                        p_dur = (len(p) / total_zh_len) * orig_dur
                        final_script.append({
                            "start": round(curr_t, 3), "end": round(curr_t + p_dur, 3),
                            "speaker": data[idx].get('speaker', 'SPEAKER_00'), "zh": p
                        })
                        curr_t += p_dur
            print(f"  -> 翻译进度: {min(i+batch_size, len(data))}/{len(data)}")
        except Exception as e:
            print(f"  ⚠️ 失败: {e}")

    out_path = r"E:\VideoTranslator_Project\separated_audio\V12_CONSTRAINED_SCRIPT.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(final_script, f, ensure_ascii=False, indent=2)
    print(f"\n🏆 标点约束版剧本已产出：{out_path}")

if __name__ == "__main__":
    run_constrained_translation()

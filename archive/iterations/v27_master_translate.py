# -*- coding: utf-8 -*-
import os, sys, json, requests, re

def run_v27_rescue_translation():
    input_json = r"E:\VideoTranslator_Project\separated_audio\v9_final_script.json"
    dotenv_path = r"C:\Users\Administrator\Desktop\HorrorAgent_Project\.env"
    
    with open(dotenv_path, "r") as f:
        api_key = [l for l in f if "SILICONFLOW_API_KEY" in l][0].split("=")[1].strip().split()[0].replace('"', '').replace("'", "")

    with open(input_json, "r", encoding="utf-8") as f: data = json.load(f)

    print(f"\n[V27-Assault] 正在执行【V26 救治级】全篇汉化...")

    final_production_script = []
    
    batch_size = 10
    for i in range(0, len(data), batch_size):
        batch = data[i:i+batch_size]
        text_payload = "\n".join([f"ID_{j+i}: {item['text']}" for j, item in enumerate(batch)])
        
        # --- 核心改进：注入 V26 救治逻辑的 Prompt ---
        prompt = f"""你是一个顶级的视频汉化导演。请将以下内容翻译成中文。
要求（V26 救治标准）：
1. 严禁翻译腔！增加口语连接词（了、以及、这些、真的是、正成为）。
2. 将长句切碎，确保每一句的物理长度适中，方便 AI 换气。
3. 【强力锁死】每一句末尾必须是“。”或“！”，绝不能是“，”。
4. 参考成功案例：将“横跨多行业产品”优化为“横跨了制造、零售。这些产品，正成为焦点！”

内容：
{text_payload}
"""
        payload = {
            "model": "deepseek-ai/DeepSeek-V3",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
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
                    # 二次语义物理切割
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
                        if len(p) < 2: continue # 过滤单字
                        p_dur = (len(p) / total_zh_len) * orig_dur
                        final_production_script.append({
                            "start": round(curr_t, 3), "end": round(curr_t + p_dur, 3),
                            "speaker": data[idx].get('speaker', 'SPEAKER_00'), "zh": p
                        })
                        curr_t += p_dur
            print(f"  -> 翻译进度: {min(i+batch_size, len(data))}/{len(data)}")
        except Exception as e:
            print(f"  ⚠️ 批次失败: {e}")

    out_path = r"E:\VideoTranslator_Project\separated_audio\V27_DIRECTOR_SCRIPT.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(final_production_script, f, ensure_ascii=False, indent=2)
    print(f"\n🏆 救治级剧本已产出：{out_path}")

if __name__ == "__main__":
    run_v27_rescue_translation()

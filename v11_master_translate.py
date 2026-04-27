# -*- coding: utf-8 -*-
import os, sys, json, requests, re, time

def run_real_full_translation():
    input_json = r"E:\VideoTranslator_Project\separated_audio\v9_final_script.json"
    dotenv_path = r"C:\Users\Administrator\Desktop\HorrorAgent_Project\.env"
    
    with open(dotenv_path, "r") as f:
        api_key = [l for l in f if "SILICONFLOW_API_KEY" in l][0].split("=")[1].strip().replace('"', '').replace("'", "")

    with open(input_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"\n[ASSAULT] 正在对全篇 {len(data)} 段进行强制汉化与语义切割...")

    final_production_script = []
    
    batch_size = 10
    for i in range(0, len(data), batch_size):
        batch = data[i:i+batch_size]
        text_payload = "\n".join([f"ID_{j}: {item['text']}" for j, item in enumerate(batch)])
        
        prompt = f"你是一个视频汉化主编。请将以下内容翻译成地道的中文解说。返回JSON数组，格式：[{{'id': 数字, 'zh': '...'}}]。\n\n内容：\n{text_payload}"
        
        payload = {
            "model": "deepseek-ai/DeepSeek-V3",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1
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
                    # --- 核心改进：翻译后立即进行语义切分 ---
                    zh_full = res['zh']
                    # 按照逗号、句号物理切分
                    sub_parts = re.split(r'([，。！？；,!?;]+)', zh_full)
                    
                    # 重新计算时间轴
                    orig_start = batch[idx]['start']
                    orig_end = batch[idx]['end']
                    orig_dur = orig_end - orig_start
                    total_zh_len = len(zh_full)
                    
                    curr_t = orig_start
                    # 重新组合标点
                    clean_parts = []
                    for k in range(0, len(sub_parts)-1, 2):
                        clean_parts.append(sub_parts[k] + sub_parts[k+1])
                    if len(sub_parts) % 2 == 1: clean_parts.append(sub_parts[-1])

                    for p in clean_parts:
                        p = p.strip()
                        if len(p) < 1: continue
                        p_dur = (len(p) / total_zh_len) * orig_dur
                        final_production_script.append({
                            "start": round(curr_t, 3),
                            "end": round(curr_t + p_dur, 3),
                            "speaker": batch[idx].get('speaker', 'SPEAKER_00'),
                            "zh": p
                        })
                        curr_t += p_dur
            print(f"  -> 已完成进度: {min(i+batch_size, len(data))}/{len(data)}")
        except Exception as e:
            print(f"  ⚠️ 失败: {e}")

    out_path = r"E:\VideoTranslator_Project\separated_audio\V11_PRODUCTION_READY.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(final_production_script, f, ensure_ascii=False, indent=2)
    print(f"\n🏆 全篇汉化与重对齐大捷！共产出 {len(final_production_script)} 个精标片段。")

if __name__ == "__main__":
    run_real_full_translation()

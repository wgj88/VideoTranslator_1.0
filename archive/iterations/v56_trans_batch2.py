# -*- coding: utf-8 -*-
import json, os, requests, re, time

def run_batch_translation(start_idx, end_idx, out_file):
    dotenv_p = r"C:\Users\Administrator\Desktop\HorrorAgent_Project\.env"
    with open(dotenv_p, "r") as f:
        api_key = [l for l in f if "SILICONFLOW_API_KEY" in l][0].split("=")[1].strip().split()[0].replace('"', '').replace("'", "")
    
    with open(r"E:\VideoTranslator_Project\unhinged_tech\RAW_EN_SCRIPT.json", "r", encoding="utf-8") as f:
        full_data = json.load(f)

    batch = full_data[start_idx:end_idx]
    print(f"\n[Part-Trans] 正在处理第 {start_idx} 到 {end_idx} 句...")

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    batch_size = 15
    translated_data = []

    for i in range(0, len(batch), batch_size):
        sub_batch = batch[i:i+batch_size]
        payload_text = "\n".join([f"ID_{j}: {item['text']}" for j, item in enumerate(sub_batch)])
        prompt = f"你是一个硬核科技导演。请将以下 2026 未来科技剧本翻译成极简、专业、幽默的中文。不带语气词，句末闭合。返回JSON数组:[{{\"zh\": \"...\"}}]\n内容:\n{payload_text}"
        
        payload = {
            "model": "deepseek-ai/DeepSeek-V3",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "response_format": {"type": "json_object"}
        }

        try:
            r = requests.post("https://api.siliconflow.cn/v1/chat/completions", json=payload, headers=headers, timeout=40).json()
            content = r['choices'][0]['message']['content']
            match = re.search(r'\[.*\]', content, re.DOTALL)
            if match:
                res_list = json.loads(match.group())
                for k, res_item in enumerate(res_list):
                    if k < len(sub_batch):
                        item = sub_batch[k]
                        translated_data.append({
                            "start": item['start'], "end": item['end'], "speaker": "SPEAKER_00",
                            "en": item['text'].strip(), "zh": res_item['zh'].strip()
                        })
            print(f"  -> 进度: {min(i+batch_size, len(batch))}/{len(batch)}")
        except Exception as e:
            print(f"  ⚠️ 失败: {e}")

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(translated_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    run_batch_translation(60, 114, r"E:\VideoTranslator_Project\unhinged_tech\PART2_ZH.json")

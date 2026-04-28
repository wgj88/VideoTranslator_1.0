# -*- coding: utf-8 -*-
import json, os, requests, re, time

def run_v2():
    input_p = r"E:\VideoTranslator_Project\unhinged_tech\offline_diarization.json"
    dotenv_p = r"C:\Users\Administrator\Desktop\HorrorAgent_Project\.env"
    
    with open(dotenv_p, "r") as f:
        api_key = [l for l in f if "SILICONFLOW_API_KEY" in l][0].split("=")[1].strip().split()[0].replace('"', '').replace("'", "")

    with open(input_p, "r", encoding="utf-8") as f: segments = json.load(f)

    print(f"\n[Translator-V2] 正在翻译 9 分钟长剧本 ({len(segments)} 句)...")

    final_script = []
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    cleaned_segments = []
    for s in segments:
        text = s['text'].strip()
        if not text or "[" in text: continue
        s['speaker'] = s.get('speaker', 'SPEAKER_00')
        cleaned_segments.append(s)

    batch_size = 15
    for i in range(0, len(cleaned_segments), batch_size):
        batch = cleaned_segments[i:i+batch_size]
        payload_text = "\n".join([f"ID_{j}: {item['text']}" for j, item in enumerate(batch)])
        
        prompt = f"你是一个硬核科技博主。请将以下内容翻译成专业利落的中文，不带语气词，句末闭合。返回JSON数组:[{{\"zh\": \"...\"}}]\n内容:\n{payload_text}"
        
        payload = {
            "model": "deepseek-ai/DeepSeek-V3",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "response_format": {"type": "json_object"}
        }

        for retry in range(3):
            try:
                r = requests.post("https://api.siliconflow.cn/v1/chat/completions", json=payload, headers=headers, timeout=30).json()
                content = r['choices'][0]['message']['content']
                match = re.search(r'\[.*\]', content, re.DOTALL)
                if match:
                    trans_list = json.loads(match.group())
                    for idx_res, res in enumerate(trans_list):
                        if idx_res < len(batch):
                            item = batch[idx_res]
                            item['zh'] = res['zh']
                            final_script.append(item)
                    print(f"  -> 进度: {min(i+batch_size, len(cleaned_segments))}/{len(cleaned_segments)}")
                    break
            except Exception as e:
                print(f"     ⚠️ 重试 {retry+1}: {e}")
                time.sleep(2)

    out_p = r"E:\VideoTranslator_Project\unhinged_tech\FINAL_CLEAN_SCRIPT.json"
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(final_script, f, ensure_ascii=False, indent=2)
    print(f"\n🏆 任务达成！汉化剧本已保存至：{out_p}")

if __name__ == "__main__":
    run_v2()

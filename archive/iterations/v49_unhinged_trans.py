# -*- coding: utf-8 -*-
import json, os, requests, re, time

def run_unhinged_translation():
    input_p = r"E:\VideoTranslator_Project\unhinged_tech\offline_diarization.json"
    dotenv_p = r"C:\Users\Administrator\Desktop\HorrorAgent_Project\.env"
    
    with open(dotenv_p, "r") as f:
        api_key = [l for l in f if "SILICONFLOW_API_KEY" in l][0].split("=")[1].strip().split()[0].replace('"', '').replace("'", "")

    with open(input_p, "r", encoding="utf-8") as f: data = json.load(f)
    segments = data['segments']

    print(f"\n[Translator] 正在对 9 分钟长剧本 ({len(segments)} 句) 执行导演级汉化...")

    final_script = []
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    # 1. 片段预清洗：合并极短句，去噪音
    cleaned_segments = []
    for s in segments:
        text = s['text'].strip()
        if not text or "[" in text or "Music" in text.lower(): continue
        s['speaker'] = s.get('speaker', 'SPEAKER_00')
        cleaned_segments.append(s)

    # 2. 分批翻译 (10句一组)
    batch_size = 10
    for i in range(0, len(cleaned_segments), batch_size):
        batch = cleaned_segments[i:i+batch_size]
        payload_text = "\n".join([f"ID_{j}: {item['text']}" for j, item in enumerate(batch)])
        
        prompt = f"""你是一个硬核科技博主。请将以下 2026 年未来科技评论翻译成地道、专业、利落的中文。
要求：
1. 风格干练，绝无语气助词。
2. 每一个返回项必须以“。”或“！”结尾。
3. 保持 JSON 格式。

内容：
{payload_text}
"""
        payload = {
            "model": "deepseek-ai/DeepSeek-V3",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "response_format": {"type": "json_object"}
        }

        try:
            r = requests.post("https://api.siliconflow.cn/v1/chat/completions", json=payload, headers=headers).json()
            content = r['choices'][0]['message']['content']
            # 解析返回
            match = re.search(r'\[.*\]', content, re.DOTALL)
            if match:
                trans_list = json.loads(match.group())
                for idx_res, res in enumerate(trans_list):
                    orig_item = batch[idx_res]
                    orig_item['zh'] = res['zh']
                    final_script.append(orig_item)
            print(f"  -> 进度: {i+batch_size}/{len(cleaned_segments)}")
        except Exception as e:
            print(f"  ⚠️ 批次失败: {e}")
            time.sleep(1)

    out_p = r"E:\VideoTranslator_Project\unhinged_tech\FINAL_CLEAN_SCRIPT.json"
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(final_script, f, ensure_ascii=False, indent=2)
    print(f"\n🏆 终极汉化剧本已就绪！共处理 {len(final_script)} 句有效台词。")

if __name__ == "__main__":
    run_unhinged_translation()

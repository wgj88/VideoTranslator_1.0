# -*- coding: utf-8 -*-
import os, sys, json, requests, re

def run_news_anchor_translation():
    input_json = r"E:\VideoTranslator_Project\separated_audio\v9_final_script.json"
    dotenv_path = r"C:\Users\Administrator\Desktop\HorrorAgent_Project\.env"
    
    with open(dotenv_path, "r") as f:
        api_key = [l for l in f if "SILICONFLOW_API_KEY" in l][0].split("=")[1].strip().replace('"', '').replace("'", "")

    with open(input_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"\n[Dehydration] 正在执行【新闻级语义脱水】重写...")

    purified_script = []
    
    # 定义要物理切除的“黑名单词汇”
    filler_blacklist = [r'\bright\b', r'\bso\b', r'\bit\b', r'\byeah\b', r'\bok\b', r'\bactually\b']

    batch_size = 10
    for i in range(0, len(data), batch_size):
        batch = data[i:i+batch_size]
        text_payload = "\n".join([f"ID_{j}: {item['text']}" for j, item in enumerate(batch)])
        
        # 强制 News Anchor Persona
        prompt = f"""你是一个顶级的【央视新闻汉化主编】。请将以下内容重塑为专业、连贯、纯净的中文解说词。
要求：
1. 彻底剔除所有语气词 (So, Right, Like, You know, OK, It)。
2. 严禁出现中英混杂，必须全中文，语气要严肃且专业。
3. 确保句子之间逻辑连贯，不要有碎片感。
4. 输出 JSON 格式：[{{"id": 数字, "zh": "..."}}]。

内容：
{text_payload}
"""
        payload = {
            "model": "deepseek-ai/DeepSeek-V3",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.05 # 降低随机性，追求极致稳定
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
                    zh_news = res['zh']
                    
                    # --- 物理级最后过滤：移除任何残留的孤立英文单词 ---
                    for pattern in filler_blacklist:
                        zh_news = re.sub(pattern, '', zh_news, flags=re.IGNORECASE)
                    zh_news = re.sub(r'[a-zA-Z]{1,2}', '', zh_news) # 移除1-2字母的英文碎片
                    zh_news = zh_news.replace("  ", " ").strip()

                    # 语义切分逻辑
                    sub_parts = re.split(r'([，。！？；]+)', zh_news)
                    orig_start, orig_dur = batch[idx]['start'], batch[idx]['end'] - batch[idx]['start']
                    
                    curr_t = orig_start
                    clean_parts = []
                    for k in range(0, len(sub_parts)-1, 2):
                        clean_parts.append(sub_parts[k] + sub_parts[k+1])
                    if len(sub_parts) % 2 == 1: clean_parts.append(sub_parts[-1])

                    for p in clean_parts:
                        p = p.strip()
                        if len(p) < 2: continue # 过滤掉单字
                        p_dur = (len(p) / len(zh_news)) * orig_dur
                        purified_script.append({
                            "start": round(curr_t, 3),
                            "end": round(curr_t + p_dur, 3),
                            "speaker": batch[idx].get('speaker', 'SPEAKER_00'),
                            "zh": p
                        })
                        curr_t += p_dur
            print(f"  -> 进度: {min(i+batch_size, len(data))}/{len(data)}")
        except Exception as e:
            print(f"  ⚠️ 失败: {e}")

    out_path = r"E:\VideoTranslator_Project\separated_audio\V12_PURIFIED_NEWS_SCRIPT.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(purified_script, f, ensure_ascii=False, indent=2)
    print(f"\n🏆 剧本脱水完成！已生成纯净版剧本：{out_path}")

if __name__ == "__main__":
    run_news_anchor_translation()

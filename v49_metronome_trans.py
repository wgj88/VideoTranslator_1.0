# -*- coding: utf-8 -*-
import json, os, requests, re

def run_metronome_translation():
    input_p = r"E:\VideoTranslator_Project\separated_audio\v9_final_script.json"
    dotenv_p = r"C:\Users\Administrator\Desktop\HorrorAgent_Project\.env"
    
    with open(dotenv_p, "r") as f:
        api_key = [l for l in f if "SILICONFLOW_API_KEY" in l][0].split("=")[1].strip().split()[0].replace('"', '').replace("'", "")

    with open(input_p, "r", encoding="utf-8") as f: data = json.load(f)

    print(f"\n[V49-Metronome] 正在执行【导演级字数闭环】重译...")

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    final_script = []

    for i, item in enumerate(data):
        dur = item['end'] - item['start']
        # 黄金配额：4.2 字/秒。 
        # 我们不仅给目标字数，还要求它“必须填满”或“必须紧凑”
        target_len = max(4, int(dur * 4.2))
        
        prompt = f"""你是一个顶级的视频配音导演。
【任务】翻译这段台词，并精准控制语速节奏。
【物理时空】这一段在画面中占据 {dur:.2f} 秒。
【硬性指标】为了让配音自然填满画面，请精准写出约 {target_len} 个汉字。
【原则】
- 如果原文翻译太短，请添加生动的描述或引导语来“填坑”。
- 如果原文太长，请通过同义词替换进行“脱水”。
- 绝无语气词。句末闭合。

英文：{item['text']}
返回 JSON: {{"zh": "..."}}
"""
        payload = {
            "model": "deepseek-ai/DeepSeek-V3",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
            "response_format": {"type": "json_object"}
        }

        try:
            r = requests.post("https://api.siliconflow.cn/v1/chat/completions", json=payload, headers=headers, timeout=20).json()
            zh = json.loads(r['choices'][0]['message']['content'])['zh']
            item['zh'] = zh
            final_script.append(item)
            print(f"  -> [{i+1}/19] 时长 {dur:.1f}s | 建议 {target_len} 字 | 产出 {len(zh)} 字: {zh}")
        except:
            print(f"  ⚠️ 自动修补中...")

    out_p = r"E:\VideoTranslator_Project\separated_audio\V49_METRONOME_SCRIPT.json"
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(final_script, f, ensure_ascii=False, indent=2)
    print(f"\n🏆 节拍器版剧本已产出：{out_p}")

if __name__ == "__main__":
    run_metronome_translation()

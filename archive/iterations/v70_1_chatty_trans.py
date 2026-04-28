# -*- coding: utf-8 -*-
import json, os, requests, time

def run_chatty_translation():
    input_p = r"E:\VideoTranslator_Project\unhinged_tech\RAW_EN_SCRIPT.json"
    dotenv_p = r"C:\Users\Administrator\Desktop\HorrorAgent_Project\.env"
    with open(dotenv_p, "r") as f:
        api_key = [l for l in f if "SILICONFLOW_API_KEY" in l][0].split("=")[1].strip().split()[0].replace('"', '').replace("'", "")
    
    with open(input_p, "r", encoding="utf-8") as f: full_data = json.load(f)
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    test_batch = [item for item in full_data if item['start'] < 120.0]
    final_script = []
    
    print(f"\n[V70.1-Chatty] 正在执行“自适应填充”重译 (前 2 分钟)...")

    for i, item in enumerate(test_batch):
        dur = item['end'] - item['start']
        # 我们给出一个“理想字数”和“最低字数”
        # 目标：保持 4.5 字/秒的舒适语速
        ideal_len = int(dur * 4.5)
        
        prompt = f"""你是一个B站科技Up主。
【任务】翻译这段台词，字数必须完美填满给定的时间。
【物理时空】这一段长达 {dur:.2f} 秒。
【字数指令】为了避免画面空转，你【必须】写出约 {ideal_len} 个汉字（绝对不能少于 {ideal_len-2} 字）。
【技巧】
- 如果原文太短，请尽可能啰嗦，增加生动的形容词、引导语（如“看吧”、“没错就是这个”）。
- 如果原文太长，请利落精简。
- 风格：地道、专业、拒绝翻译腔。
原文：{item['text']}
返回 JSON: {{"zh": "..."}}
"""
        success = False
        for retry in range(8): # 加强重试
            try:
                r = requests.post("https://api.siliconflow.cn/v1/chat/completions", json={
                    "model": "deepseek-ai/DeepSeek-V3",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.4, "response_format": {"type": "json_object"}
                }, headers=headers, timeout=15).json()
                zh = json.loads(r['choices'][0]['message']['content'])['zh']
                item['zh'] = zh
                final_script.append(item)
                print(f"  -> [{i+1}] 空间:{dur:.1f}s | 指标:{ideal_len}字 | 产出:{len(zh)}字: {zh}")
                success = True
                break
            except:
                time.sleep(1)
        if not success: final_script.append(item)

    out_p = r"E:\VideoTranslator_Project\unhinged_tech\V70_1_CHATTY_SCRIPT.json"
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(final_script, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    run_chatty_translation()

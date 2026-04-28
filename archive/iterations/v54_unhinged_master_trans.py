# -*- coding: utf-8 -*-
import json, os, requests, time

def run_grand_translation():
    input_p = r"E:\VideoTranslator_Project\unhinged_tech\RAW_EN_SCRIPT.json"
    dotenv_p = r"C:\Users\Administrator\Desktop\HorrorAgent_Project\.env"
    with open(dotenv_p, "r") as f:
        api_key = [l for l in f if "SILICONFLOW_API_KEY" in l][0].split("=")[1].strip().split()[0].replace('"', '').replace("'", "")
    
    with open(input_p, "r", encoding="utf-8") as f: full_data = json.load(f)
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    # 核心资产配置
    CPS = 5.06
    final_calibrated_script = []
    
    print(f"\n[Master-Translator] 正在为 114 段台词裁制“5.06 CPS”外衣...")

    # 我们分大批次处理，每批 20 句
    for i, item in enumerate(full_data):
        dur = item['end'] - item['start']
        target_len = max(4, int(dur * CPS))
        
        prompt = f"你是一个科技导演。请将 '{item['text']}' 翻译成约 {target_len} 个汉字的利落中文。要求：必须接近目标字数以填满时间轴。返回格式:{{'zh': '...'}}"
        
        success = False
        for retry in range(5):
            try:
                r = requests.post("https://api.siliconflow.cn/v1/chat/completions", json={
                    "model": "deepseek-ai/DeepSeek-V3",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1, "response_format": {"type": "json_object"}
                }, headers=headers, timeout=15).json()
                zh = json.loads(r['choices'][0]['message']['content'])['zh']
                item['zh'] = zh
                item['target_len'] = target_len
                final_calibrated_script.append(item)
                print(f"  -> [{i+1}/114] 对齐成功 (字数:{len(zh)})")
                success = True
                break
            except:
                time.sleep(0.5)
        
        if not success:
            item['zh'] = "。 " # 最终失败则使用占位符
            final_calibrated_script.append(item)

    out_p = r"E:\VideoTranslator_Project\unhinged_tech\UNHINGED_FINAL_506_SCRIPT.json"
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(final_calibrated_script, f, ensure_ascii=False, indent=2)
    print(f"\n🏆 全篇 114 段导演级剧本已构建完成：{out_p}")

if __name__ == "__main__":
    run_grand_translation()

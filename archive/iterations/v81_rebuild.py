# -*- coding: utf-8 -*-
import json, requests, os, re, sys

def run_v81_force_build():
    print("🚀 启动 V81 剧本深度导演程序...")
    input_p = r"E:\VideoTranslator_Project\unhinged_tech\RAW_EN_SCRIPT.json"
    dotenv_p = r"C:\Users\Administrator\Desktop\HorrorAgent_Project\.env"
    
    try:
        with open(dotenv_p, "r") as f:
            api_key = [l for l in f if "SILICONFLOW_API_KEY" in l][0].split("=")[1].strip().strip("'").strip('"').split()[0]
    except Exception as e:
        print(f"❌ Key 加载失败: {e}")
        return

    with open(input_p, "r", encoding="utf-8") as f: data = json.load(f)
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    test_batch = [it for it in data if it['start'] < 60]
    final_script = []

    for i, item in enumerate(test_batch):
        dur = item['end'] - item['start']
        # V81 严格脱水字数计算
        max_chars = int((dur - 0.2) * 4.5) # 进一步降到 4.5 CPS 确保绝对不追尾
        
        prompt = f"你是一个毒舌科技博主。请将 '{item['text']}' 译为地道中文。要求：字数必须少于 {max_chars} 个汉字，包含标点（，。！？），数字全汉字，语气利落。返回JSON: {{'zh': '...'}}"
        
        try:
            r = requests.post("https://api.siliconflow.cn/v1/chat/completions", json={
                "model": "deepseek-ai/DeepSeek-V3", "messages": [{"role": "user", "content": prompt}], "temperature": 0.2
            }, headers=headers, timeout=25).json()
            
            raw_text = r['choices'][0]['message']['content']
            zh = json.loads(re.search(r"\{.*\}", raw_text, re.DOTALL).group())['zh']
            print(f"  [{i+1}/13] {zh}")
            item['zh'] = zh
            final_script.append(item)
        except Exception as e:
            print(f"  ⚠️ 段落 {i+1} 失败: {e}")
            item['zh'] = "翻译失败，请检查。"
            final_script.append(item)

    with open(r"E:\VideoTranslator_Project\unhinged_tech\V81_60S_FINAL.json", "w", encoding="utf-8") as f:
        json.dump(final_script, f, ensure_ascii=False, indent=2)
    print("\n✅ V81 一分钟剧本铸造完成！")

if __name__ == "__main__":
    run_v81_force_build()

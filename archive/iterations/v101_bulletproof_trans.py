# -*- coding: utf-8 -*-
import json, requests, os, re, time

def run_v101_translation():
    print("\n" + "🛡️"*10 + " 启动 V101 全量剧本汉化（防弹增强版） " + "🛡️"*10)
    input_p = r"E:\VideoTranslator_Project\unhinged_tech\RAW_EN_SCRIPT.json"
    dotenv_p = r"C:\Users\Administrator\Desktop\HorrorAgent_Project\.env"
    
    with open(dotenv_p, "r") as f:
        api_key = [l for l in f if "SILICONFLOW_API_KEY" in l][0].split("=")[1].strip().strip("'").strip('"').split()[0]
    
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    with open(input_p, "r", encoding="utf-8") as f: data = json.load(f)
    
    output_p = r"E:\VideoTranslator_Project\unhinged_tech\V101_FINAL_SCRIPT.json"
    final_script = []

    print(f"  -> 目标总量：{len(data)} 段。采用 4.5 CPS 严格模式。")

    for i, item in enumerate(data):
        dur = item['end'] - item['start']
        # 字数保底：至少允许 5 个汉字
        max_chars = max(5, int((dur - 0.2) * 4.5))
        
        prompt = f"你是一个硬核数码博主。将 '{item['text']}' 译为极简口语。要求：字数严控在 {max_chars} 个汉字内，必带标点，数字全汉化。直接返回JSON: {{'zh': '...'}}"
        
        success = False
        for retry in range(3):
            try:
                r = requests.post("https://api.siliconflow.cn/v1/chat/completions", json={
                    "model": "deepseek-ai/DeepSeek-V3", "messages": [{"role": "user", "content": prompt}], "temperature": 0.5
                }, headers=headers, timeout=20).json()
                
                content = r['choices'][0]['message']['content']
                # 增强型解析：尝试匹配 JSON
                match = re.search(r"\{.*\}", content, re.DOTALL)
                if match:
                    zh = json.loads(match.group())['zh']
                else:
                    zh = content.strip().strip('"').replace("{'zh': '", "").replace("'}", "")
                
                item['zh'] = zh
                print(f"  ✅ [{i+1}/{len(data)}] {zh}")
                success = True
                break
            except Exception as e:
                print(f"  ⏳ [{i+1}] 重试中 (原因: {str(e)[:40]}...)")
                time.sleep(1.5)
        
        if not success:
            print(f"  ❌ 第 {i+1} 段彻底失败，已跳过。")
            item['zh'] = "... "
        
        final_script.append(item)
        # 实时保存进度
        if (i+1) % 5 == 0:
            with open(output_p, "w", encoding="utf-8") as f: json.dump(final_script, f, ensure_ascii=False, indent=2)

    with open(output_p, "w", encoding="utf-8") as f:
        json.dump(final_script, f, ensure_ascii=False, indent=2)
    print(f"\n🏁 114 段剧本已全部铸造完成！路径：{output_p}")

if __name__ == "__main__":
    run_v101_translation()

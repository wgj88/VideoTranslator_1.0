# -*- coding: utf-8 -*-
import json, requests, os, re, time

def run_v99_recovery():
    print("\n" + "🩹"*10 + " 启动 V99 全量剧本断点修复（114段） " + "🩹"*10)
    input_p = r"E:\VideoTranslator_Project\unhinged_tech\RAW_EN_SCRIPT.json"
    dotenv_p = r"C:\Users\Administrator\Desktop\HorrorAgent_Project\.env"
    with open(dotenv_p, "r") as f:
        api_key = [l for l in f if "SILICONFLOW_API_KEY" in l][0].split("=")[1].strip().strip("'").strip('"').split()[0]
    
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    with open(input_p, "r", encoding="utf-8") as f: data = json.load(f)
    
    output_p = r"E:\VideoTranslator_Project\unhinged_tech\V99_FULL_RECOVERY.json"
    # 如果已有部分进度，加载它
    if os.path.exists(output_p):
        with open(output_p, "r", encoding="utf-8") as f: recovered_data = json.load(f)
    else:
        recovered_data = []

    existing_ids = {it['id'] for it in recovered_data if it.get('zh') and it['zh'] != "... "}

    print(f"  -> 当前进度：{len(existing_ids)}/114。开始补全剩余段落...")

    for i, item in enumerate(data):
        if item['id'] in existing_ids: continue # 跳过已完成的

        dur = item['end'] - item['start']
        max_chars = int((dur - 0.2) * 4.5)
        
        prompt = f"你是一个硬核数码区UP主。将 '{item['text']}' 译为地道中文，少于 {max_chars} 字，数字全汉字，语气利落。直接返回JSON: {{'zh': '...'}}"
        
        success = False
        print(f"  [Processing] 段落 {i+1}/114...", end="\r")
        for retry in range(3): # 增加到3次重试
            try:
                r = requests.post("https://api.siliconflow.cn/v1/chat/completions", json={
                    "model": "deepseek-ai/DeepSeek-V3", "messages": [{"role": "user", "content": prompt}], "temperature": 0.4
                }, headers=headers, timeout=15).json()
                
                content = r['choices'][0]['message']['content']
                zh = json.loads(re.search(r"\{.*\}", content, re.DOTALL).group())['zh']
                item['zh'] = zh
                recovered_data.append(item)
                success = True
                # 每成功10个保存一次
                if len(recovered_data) % 10 == 0:
                    with open(output_p, "w", encoding="utf-8") as f: json.dump(recovered_data, f, ensure_ascii=False, indent=2)
                break
            except Exception as e:
                time.sleep(1)
        
        if not success:
            print(f"\n  ❌ 第 {i+1} 段多次重试失败，记录为空。")
            item['zh'] = "... "
            recovered_data.append(item)

    # 最终保存
    recovered_data.sort(key=lambda x: x['id'])
    with open(output_p, "w", encoding="utf-8") as f:
        json.dump(recovered_data, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 114 段灵魂剧本全量铸造完成！路径：{output_p}")

if __name__ == "__main__":
    run_v99_recovery()

# -*- coding: utf-8 -*-
import json, requests, os

def refine_for_voxcpm():
    input_p = r"E:\VideoTranslator_Project\unhinged_tech\UNHINGED_FINAL_506_SCRIPT.json"
    dotenv_p = r"C:\Users\Administrator\Desktop\HorrorAgent_Project\.env"
    with open(dotenv_p, "r") as f:
        api_key = [l for l in f if "SILICONFLOW_API_KEY" in l][0].split("=")[1].strip().split()[0].replace('"', '').replace("'", "")
    
    with open(input_p, "r", encoding="utf-8") as f: data = json.load(f)
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    print("\n--- ✍️ 正在执行【VoxCPM 亲和力】剧本重塑 ---")

    for i in range(5): # 测试前 5 句
        text = data[i]['zh']
        prompt = f"""你是一个配音剧本专家。请将以下中文台词重写为“AI配音亲和格式”。
要求：
1. 【数字/缩写全汉化】：将 $3,500 转为“三千五百美元”，GPU 转为“图形处理器”等。
2. 【呼吸控制】：在长句中间合适位置插入 [pause] 标签。
3. 【断句强化】：多用句号，减少长逗号，确保 AI 换气。
4. 字数必须维持在原长度（约 {len(text)} 字）。

原始台词：{text}
返回 JSON: {{"refined_zh": "..."}}
"""
        r = requests.post("https://api.siliconflow.cn/v1/chat/completions", json={
            "model": "deepseek-ai/DeepSeek-V3",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"}
        }, headers=headers).json()
        
        refined = json.loads(r['choices'][0]['message']['content'])['refined_zh']
        print(f"  -> [{i+1}] 之前: {text}")
        print(f"     之后: {refined}")
        data[i]['zh'] = refined

    with open(r"E:\VideoTranslator_Project\unhinged_tech\V70_REFINED_SCRIPT.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    refine_for_voxcpm()

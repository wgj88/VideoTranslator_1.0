# -*- coding: utf-8 -*-
import os, json, requests, re

def run_stage4_translation():
    script_path = r"E:\VideoTranslator_Project\separated_audio\v9_final_script.json"
    
    # 物理读取 API Key
    dotenv_path = r"C:\Users\Administrator\Desktop\HorrorAgent_Project\.env"
    api_key = None
    with open(dotenv_path, "r", encoding="utf-8") as f:
        for line in f:
            if "SILICONFLOW_API_KEY" in line:
                api_key = line.split("=")[1].strip().replace('"', '').replace("'", "")
    
    if not api_key:
        print("❌ 找不到 API Key")
        return

    with open(script_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"\n[Stage 4] 正在调用 DeepSeek-V3 进行【多角色同步翻译】...")

    # 我们将全篇分批发送给 LLM
    batch_size = 15
    for i in range(0, len(data), batch_size):
        batch = data[i:i+batch_size]
        text_to_translate = "\n".join([f"ID_{j}: [{item['speaker']}] {item['text']}" for j, item in enumerate(batch)])
        
        prompt = f"""你是一个顶级的视频汉化主编。请将以下台词翻译成地道的中文。
要求：
1. 保持口语化，适合短视频解说。
2. 每一个片段返回一个 JSON 对象，格式：{{"id": 0, "zh": "...", "style": "..."}}。
3. 'style' 必须根据 speaker 的性别和语气分配：
   - 女性：'(A clear female voice)' 
   - 男性：'(A calm and professional male voice)'
   
待翻译内容：
{text_to_translate}

请只返回 JSON 数组，不要任何解释。
"""
        payload = {
            "model": "deepseek-ai/DeepSeek-V3",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
            "response_format": {"type": "json_object"}
        }
        
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        try:
            r = requests.post("https://api.siliconflow.cn/v1/chat/completions", json=payload, headers=headers, timeout=60).json()
            content = r['choices'][0]['message']['content']
            
            # 暴力提取 JSON
            match = re.search(r'\[.*\]', content, re.DOTALL)
            if match:
                res_list = json.loads(match.group())
                for res in res_list:
                    idx = int(res['id'])
                    if idx < len(batch):
                        batch[idx]['zh'] = res['zh']
                        batch[idx]['style'] = res['style']
                        print(f"  -> [{batch[idx]['speaker']}] {batch[idx]['zh'][:20]}...")
        except Exception as e:
            print(f"  ⚠️ 批处理失败: {e}")

    zh_out = script_path.replace(".json", "_zh_localized.json")
    with open(zh_out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"🏆 第四阶段完成：汉化剧本已生成 {zh_out}")

if __name__ == "__main__":
    run_stage4_translation()

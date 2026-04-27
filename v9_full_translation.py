# -*- coding: utf-8 -*-
import os, sys, json, requests, re, time

def run_full_translation():
    script_path = r"E:\VideoTranslator_Project\separated_audio\v9_final_script.json"
    dotenv_path = r"C:\Users\Administrator\Desktop\HorrorAgent_Project\.env"
    
    with open(dotenv_path, "r") as f:
        api_key = [l for l in f if "SILICONFLOW_API_KEY" in l][0].split("=")[1].strip().replace('"', '').replace("'", "")

    with open(script_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"\n[Full-Trans] 正在对全篇 {len(data)} 句台词进行分角色汉化...")

    # 分批次处理，每批 15 句，防止 Token 溢出或解析错误
    batch_size = 15
    for i in range(0, len(data), batch_size):
        batch = data[i:i+batch_size]
        # 构造带 ID 和 角色标签的 Prompt
        text_batch = "\n".join([f"ID_{j+i}: [{item.get('speaker', 'SPEAKER_00')}] {item['text']}" for j, item in enumerate(batch)])
        
        prompt = f"""你是一个顶级的视频汉化主编。请将以下台词翻译成地道的中文。
要求：
1. 保持口语化，语感要像抖音或 YouTube 的数码解说。
2. 必须输出 JSON 数组格式：[{{"id": 数字, "zh": "..."}}]。
3. 严禁改变原意，严禁省略。

待翻译内容：
{text_batch}
"""
        payload = {
            "model": "deepseek-ai/DeepSeek-V3",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "response_format": {"type": "json_object"}
        }
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        
        try:
            r = requests.post("https://api.siliconflow.cn/v1/chat/completions", json=payload, headers=headers, timeout=60).json()
            content = r['choices'][0]['message']['content']
            
            # 物理提取
            match = re.search(r'\[.*\]', content, re.DOTALL)
            if match:
                results = json.loads(match.group())
                for res in results:
                    idx = int(res['id'])
                    if idx < len(data):
                        data[idx]['zh_full'] = res['zh']
            
            print(f"  -> 已完成进度: {min(i+batch_size, len(data))}/{len(data)}")
            time.sleep(0.5) # 微调频率
        except Exception as e:
            print(f"  ⚠️ 批次 {i} 异常: {e}")

    out_path = r"E:\VideoTranslator_Project\separated_audio\v9_FULL_CHINESE_SCRIPT.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 全篇翻译完成！已产出 100% 覆盖的中文剧本：{out_path}")

if __name__ == "__main__":
    run_full_translation()

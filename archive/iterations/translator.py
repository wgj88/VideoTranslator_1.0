# -*- coding: utf-8 -*-
import json, os, requests, re

class VideoTranslator:
    def __init__(self):
        with open(r"C:\Users\Administrator\Desktop\HorrorAgent_Project\.env", "r") as f:
            self.api_key = [l for l in f if "SILICONFLOW_API_KEY" in l][0].split("=")[1].strip().split()[0]
        self.base_url = "https://api.siliconflow.cn/v1/chat/completions"

    def translate_json(self, json_path):
        print(f"\n[Translator] 正在进行最后一次质量冲刺...")
        with open(json_path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)

        batch = data[:10]
        text = "\n".join([f"ID_{i}: {d['text']}" for i, d in enumerate(batch)])
        prompt = f"你是一个视频汉化主编。请将以下内容翻译成中文解说。返回JSON数组，每个对象包含index, zh, style。(style统一用 '(A calm and professional male voice)')。\n\n内容：\n{text}"
        
        payload = {"model": "deepseek-ai/DeepSeek-V3", "messages": [{"role": "user", "content": prompt}], "temperature": 0.1}
        r = requests.post(self.base_url, json=payload, headers={"Authorization": f"Bearer {self.api_key}"}).json()
        content = r['choices'][0]['message']['content']
        
        match = re.search(r'\[.*\]', content, re.DOTALL)
        if match:
            res_list = json.loads(match.group())
            for r in res_list:
                idx = int(str(r.get('index', r.get('idx', 0))).replace("ID_", ""))
                if idx < len(batch):
                    batch[idx]['translated_text'] = f"{r.get('style', '(A voice)')}{r['zh']}"
                    print(f"  -> {batch[idx]['translated_text']}")
        
        zh_json = json_path.replace(".json", "_zh.json")
        with open(zh_json, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return zh_json

if __name__ == "__main__":
    print("Translator Surgery Done.")

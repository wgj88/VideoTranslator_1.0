# -*- coding: utf-8 -*-
import json, os, requests

class VideoTranslator:
    def __init__(self):
        self.api_key = self._load_env_key(r"C:\Users\Administrator\Desktop\HorrorAgent_Project\.env")
        self.base_url = "https://api.siliconflow.cn/v1/chat/completions"
        
    def _load_env_key(self, path):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if "SILICONFLOW_API_KEY" in line:
                    return line.split("=")[1].strip().split()[0]
        return None

    def translate_json(self, json_path):
        print(f"\n[Translator] 正在通过 DeepSeek-V3 进行高质量汉化...")
        with open(json_path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)

        batch = data[:5] # 演示期只处理前 5 句
        text_to_translate = "\n".join([f"ID_{idx}: {item['text']}" for idx, item in enumerate(batch)])
        
        prompt = f"你是一个视频汉化专家。请将以下印地语/英语混合的内容翻译成地道的中文解说。返回JSON数组，每个对象包含index, zh, style。(style统一用 '(A calm and professional male voice)')。\n\n内容：\n{text_to_translate}"
        
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"model": "deepseek-ai/DeepSeek-V3", "messages": [{"role": "user", "content": prompt}], "temperature": 0.1}
        
        try:
            resp = requests.post(self.base_url, json=payload, timeout=60).json()
            content = resp['choices'][0]['message']['content']
            if "```json" in content: content = content.split("```json")[1].split("```")[0]
            
            # 强化鲁棒性的解析逻辑
            res = json.loads(content)
            if isinstance(res, dict): 
                # 如果返回的是 {"results": [...]}
                for key in res:
                    if isinstance(res[key], list):
                        res = res[key]
                        break

            for r in res:
                idx = int(str(r.get('index', r.get('id', 0))).replace("ID_", ""))
                if idx < len(batch):
                    batch[idx]['translated_text'] = f"{r.get('style', '(A voice)')}{r['zh']}"
                    print(f"  [Trans] {batch[idx]['translated_text']}")
        except Exception as e:
            print(f"  [Error] {e}")

        zh_json_path = json_path.replace(".json", "_zh.json")
        with open(zh_json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return zh_json_path

if __name__ == "__main__":
    vt = VideoTranslator()
    vt.translate_json(r'E:\VideoTranslator_Project\raw_videos\8 EASY Faceless YouTube Channel Ideas for 2026 (High RPM + Views).json')

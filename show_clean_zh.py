import requests, json, os
with open(r"C:\Users\Administrator\Desktop\HorrorAgent_Project\.env", "r") as f:
    key = [l for l in f if "SILICONFLOW_API_KEY" in l][0].split("=")[1].strip().split()[0]

json_path = r'E:\VideoTranslator_Project\raw_videos\15 Coolest Gadgets on Amazon You’ll Wish You Had Sooner.f140.json'
with open(json_path, "r", encoding="utf-8-sig") as f:
    data = json.load(f)[:5]

text = "\n".join([f"{i}: {d['text']}" for i, d in enumerate(data)])
payload = {
    "model": "deepseek-ai/DeepSeek-V3",
    "messages": [{"role": "user", "content": f"请将这些数码产品解说翻译成地道的中文解说短句。返回JSON数组，格式：[{{'idx': 0, 'zh': '...'}}]。\n\n内容：\n{text}"}]
}
r = requests.post("https://api.siliconflow.cn/v1/chat/completions", json=payload, headers={"Authorization": f"Bearer {key}"})
print(r.json()['choices'][0]['message']['content'])

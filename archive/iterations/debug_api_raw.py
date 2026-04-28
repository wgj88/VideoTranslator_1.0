import requests, os
with open(r"C:\Users\Administrator\Desktop\HorrorAgent_Project\.env", "r") as f:
    api_key = [line for line in f if "SILICONFLOW_API_KEY" in line][0].split("=")[1].strip().split()[0]
url = "https://api.siliconflow.cn/v1/chat/completions"
headers = {"Authorization": f"Bearer {api_key}"}
payload = {"model": "deepseek-ai/DeepSeek-V3", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 10}
r = requests.post(url, json=payload, headers=headers)
print(f"Status: {r.status_code}")
print(f"Content: {r.text}")

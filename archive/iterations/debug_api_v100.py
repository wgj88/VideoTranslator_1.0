# -*- coding: utf-8 -*-
import requests, json

def debug_siliconflow():
    dotenv_p = r"C:\Users\Administrator\Desktop\HorrorAgent_Project\.env"
    try:
        with open(dotenv_p, "r") as f:
            line = [l for l in f if "SILICONFLOW_API_KEY" in l][0]
            api_key = line.split("=")[1].strip().strip("'").strip('"').split()[0]
            print(f"🔍 调试：提取到的 Key 前几位: {api_key[:8]}...")
    except Exception as e:
        print(f"❌ Key 加载物理失败: {e}")
        return

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    test_payload = {
        "model": "deepseek-ai/DeepSeek-V3",
        "messages": [{"role": "user", "content": "hi"}],
        "max_tokens": 10
    }
    
    print("📡 正在尝试连接硅基流动服务器...")
    try:
        r = requests.post("https://api.siliconflow.cn/v1/chat/completions", json=test_payload, headers=headers, timeout=10)
        print(f"📜 状态码: {r.status_code}")
        print(f"📝 原始响应: {r.text}")
    except Exception as e:
        print(f"💥 网络请求层崩溃: {e}")

if __name__ == "__main__":
    debug_siliconflow()

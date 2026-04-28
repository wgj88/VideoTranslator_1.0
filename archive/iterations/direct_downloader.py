# -*- coding: utf-8 -*-
import requests, os

URLS = {
    "torchaudio-2.11.0.dev20260408+cu128-cp313-cp313-win_amd64.whl": "https://download.pytorch.org/whl/nightly/cu128/torchaudio-2.11.0.dev20260408%2Bcu128-cp313-cp313-win_amd64.whl",
    "torchvision-0.23.0.dev20260408+cu128-cp313-cp313-win_amd64.whl": "https://download.pytorch.org/whl/nightly/cu128/torchvision-0.23.0.dev20260408%2Bcu128-cp313-cp313-win_amd64.whl"
}

# 🚀 伪装成真实的 macOS Chrome 用户
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
proxies = {"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}

def download():
    print("--- 🚀 开始【伪装模式】收割 Blackwell 配套包 ---")
    for name, url in URLS.items():
        print(f"  正在潜行抓取: {name}...")
        try:
            r = requests.get(url, headers=headers, proxies=proxies, timeout=120, stream=True)
            r.raise_for_status()
            with open(name, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024*1024): # 1MB 分块
                    f.write(chunk)
            print(f"  ✅ {name} 成功收入囊中！")
        except Exception as e:
            print(f"  ❌ 依然被阻断: {e}")

if __name__ == "__main__":
    download()

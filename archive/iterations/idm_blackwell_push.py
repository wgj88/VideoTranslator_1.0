# -*- coding: utf-8 -*-
import os, subprocess

IDM_PATH = r"C:\Program Files (x86)\Internet Download Manager\IDMan.exe"
TARGET_DIR = r"C:\Users\Administrator\Desktop\VideoTranslator_Project"

# 🚀 针对 Python 3.13 + CUDA 12.8 (Blackwell) 的直连地址
URLS = [
    "https://download.pytorch.org/whl/nightly/cu128/torch-2.12.0.dev20260408%2Bcu128-cp313-cp313-win_amd64.whl",
    "https://download.pytorch.org/whl/nightly/cu128/torchaudio-2.11.0.dev20260408%2Bcu128-cp313-cp313-win_amd64.whl",
    "https://download.pytorch.org/whl/nightly/cu128/torchvision-0.23.0.dev20260408%2Bcu128-cp313-cp313-win_amd64.whl"
]

def push_to_idm():
    if not os.path.exists(IDM_PATH):
        print("❌ 未找到 IDM 主程序")
        return

    print("--- 🚀 正在将 Blackwell 驱动包推送至 IDM 队列 ---")
    for url in URLS:
        file_name = url.split("/")[-1].replace("%2B", "+")
        # /d URL /p 路径 /f 文件名 /n 静默添加 /q 立即开始
        cmd = [IDM_PATH, "/d", url, "/p", TARGET_DIR, "/f", file_name, "/n", "/q"]
        subprocess.run(cmd)
        print(f"  + 已推送: {file_name}")

    print("\n✅ 推送完毕！请在 IDM 中等待下载完成（总计约 3GB）。")

if __name__ == "__main__":
    push_to_idm()

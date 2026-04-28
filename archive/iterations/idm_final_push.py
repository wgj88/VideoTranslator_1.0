# -*- coding: utf-8 -*-
import os, subprocess

IDM_PATH = r"C:\Program Files (x86)\Internet Download Manager\IDMan.exe"
TARGET_DIR = r"C:\Users\Administrator\Desktop\VideoTranslator_Project"

URLS = [
    "https://download.pytorch.org/whl/nightly/cu128/torchaudio-2.11.0.dev20260408%2Bcu128-cp313-cp313-win_amd64.whl",
    "https://download.pytorch.org/whl/nightly/cu128/torchvision-0.23.0.dev20260408%2Bcu128-cp313-cp313-win_amd64.whl"
]

def push():
    for url in URLS:
        file_name = url.split("/")[-1].replace("%2B", "+")
        cmd = [IDM_PATH, "/d", url, "/p", TARGET_DIR, "/f", file_name, "/n", "/q"]
        subprocess.run(cmd)
        print(f"  + 已推送: {file_name}")

if __name__ == "__main__":
    push()
    print("\n✅ 推送成功！请在 IDM 中启动下载。")

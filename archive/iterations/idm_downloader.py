# -*- coding: utf-8 -*-
import os, subprocess

# 🚀 常见的 IDM 安装路径
IDM_PATH = r"C:\Program Files (x86)\Internet Download Manager\IDMan.exe"
TARGET_DIR = r"C:\Users\Administrator\Desktop\VideoTranslator_Project\model_weights"

# VoxCPM2 核心权重文件列表 (Hugging Face 直连)
BASE_URL = "https://huggingface.co/openbmb/VoxCPM2/resolve/main/"
FILES = [
    "model.safetensors",
    "config.json",
    "generation_config.json",
    "tokenizer.json",
    "tokenizer_config.json",
    "vocoder.safetensors",
    "audio_vae_v2.safetensors"
]

def add_to_idm():
    if not os.path.exists(IDM_PATH):
        print(f"❌ 错误：未在 {IDM_PATH} 找到 IDM，请检查安装路径。")
        return

    print(f"--- 🚀 正在将 {len(FILES)} 个模型文件推送至 IDM ---")
    for file_name in FILES:
        url = BASE_URL + file_name
        # IDM 命令行参数: /d URL /p 路径 /f 文件名 /n (静默添加) /q (开始下载)
        cmd = [IDM_PATH, "/d", url, "/p", TARGET_DIR, "/f", file_name, "/n", "/q"]
        subprocess.run(cmd)
        print(f"  + 已推送: {file_name}")

    print("\n✅ 推送完成！请在 IDM 窗口中确认下载进度。")
    print(f"📁 下载完成后，请确保所有文件都在: {TARGET_DIR}")

if __name__ == "__main__":
    add_to_idm()

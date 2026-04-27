# -*- coding: utf-8 -*-
from huggingface_hub import snapshot_download
import os

def fast_download():
    repo_id = "openbmb/VoxCPM2"
    local_dir = r"C:\Users\Administrator\Desktop\VideoTranslator_Project\model_weights"
    os.makedirs(local_dir, exist_ok=True)
    
    print(f"--- 🚀 正在通过 Xet 协议极速下载 {repo_id} ---")
    print("系统将自动启用分块并发下载...")
    
    # snapshot_download 会自动检测并调用已安装的 hf_xet
    path = snapshot_download(
        repo_id=repo_id,
        local_dir=local_dir,
        local_dir_use_symlinks=False,
        proxies={"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}
    )
    
    print(f"\n✅ 下载完成！权重已固化至: {path}")

if __name__ == "__main__":
    fast_download()

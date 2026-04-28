# -*- coding: utf-8 -*-
import os, sys, torch

def check_local_vad():
    print("\n--- 🔍 正在执行【VAD 资产大搜寻】 ---")
    
    # 尝试 1: 通过 whisperx 内部接口加载 (它通常带有本地封装)
    try:
        from whisperx.vad import load_vad_model
        # 尝试加载到 GPU，不带网络认证
        vad_model = load_vad_model("cuda", use_auth_token=None)
        print("✅ 成功！已通过 whisperx 接口锁定本地 Silero VAD 引擎。")
        return True
    except Exception as e:
        print(f"  ❌ 尝试 1 失败: {e}")

    # 尝试 2: 扫描用户的 HuggingFace 缓存目录
    cache_dir = r"C:\Users\Administrator\.cache\huggingface\hub"
    if os.path.exists(cache_dir):
        print(f"  -> 正在扫描 HF 缓存: {cache_dir}")
        for root, dirs, files in os.walk(cache_dir):
            for f in files:
                if "silero_vad" in f.lower():
                    print(f"🎯 发现疑似 VAD 权重: {os.path.join(root, f)}")
                    return True

    print("⚠️ 结论：未在预设路径发现激活的 VAD 模型。")
    return False

if __name__ == "__main__":
    check_local_vad()

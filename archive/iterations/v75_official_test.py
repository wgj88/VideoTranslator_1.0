# -*- coding: utf-8 -*-
import os, sys, requests, soundfile as sf, time, whisper, subprocess

FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

def run_v75_official_style():
    print("\n" + "📜"*10 + " 启动 V75 官方正统对齐方案 " + "📜"*10)
    
    # 核心数据：前 5 句
    script = [
        {"id": 1, "dur": 5.8, "zh": "现在是二零二六年。你那台价值三千五百美元的智能冰箱居然带显卡。"},
        {"id": 2, "dur": 5.2, "zh": "你老板是人工智能。女友是机器人。每个创业项目听着都像优步变种。"},
        {"id": 3, "dur": 5.4, "zh": "量子科技。欢迎来到未来。这里全是过度设计的测试版。"},
        {"id": 4, "dur": 4.5, "zh": "现在。是时候开启我车库里的年度传统了。我要唤醒那个装在罐子里的先知。"},
        {"id": 5, "dur": 4.3, "zh": "今年科技圈要炸。去年我曾精准预言。人工智能助手将会席卷全球。"}
    ]
    
    seed_p = r"E:\VideoTranslator_Project\unhinged_tech\seeds\V73_SURGICAL_SEED.wav"
    # 重要：种子音频对应的英文原文 (It's the year 2026. Your $3,500 smart fridge...)
    seed_text = "It's the year 2026. Your $3,500 smart fridge has a GPU and it's showing you ads."
    
    for item in script:
        # 1. 动态语气引导词
        # 根据字数密度自动选择策略 (此处演示写死为稳健模式)
        steered_text = "(Standard speech speed) " + item['zh'] + "。"
        
        save_p = f"E:\\VideoTranslator_Project\\temp_factory\\v75_raw_{item['id']}.wav"
        
        # 2. 官方推荐调用：带上 prompt_text 提高保真度
        requests.post("http://127.0.0.1:8000/generate", json={
            "text": steered_text,
            "ref_wav": seed_p,
            "prompt_text": seed_text, # <--- V75 核心改动
            "save_path": save_p
        }, timeout=100, proxies={"http": None, "https": None})
        
        y, sr = sf.read(save_p)
        print(f"  -> [{item['id']}] 生成成功 | 时长: {len(y)/sr:.2f}s | 预期: {item['dur']:.1f}s")

if __name__ == "__main__":
    run_v75_official_style()

# -*- coding: utf-8 -*-
import os, requests, soundfile as sf, time

def run_v76_steering_test():
    print("\n" + "🏎️"*10 + " 启动 V76 指令级语速干预 " + "🏎️"*10)
    
    # 我们针对溢出最严重的第 04 段做实验
    # 目标：从 7.2s 压回到 4.5s
    test_cases = [
        {"id": 4, "dur": 4.5, "zh": "现在。是时候开启我车库里的年度传统了。我要唤醒那个装在罐子里的先知。", "mode": "(Speaking fast)"},
        {"id": 5, "dur": 4.3, "zh": "今年科技圈要炸。去年我曾精准预言。人工智能助手将会席卷全球。", "mode": "(Speaking fast)"}
    ]
    
    seed_p = r"E:\VideoTranslator_Project\unhinged_tech\seeds\V73_SURGICAL_SEED.wav"
    seed_text = "It's the year 2026. Your $3,500 smart fridge has a GPU and it's showing you ads."
    
    for item in test_cases:
        steered_text = item['mode'] + " " + item['zh'] + "。"
        save_p = f"E:\\VideoTranslator_Project\\temp_factory\\v76_steer_{item['id']}.wav"
        
        requests.post("http://127.0.0.1:8000/generate", json={
            "text": steered_text,
            "ref_wav": seed_p,
            "prompt_text": seed_text,
            "save_path": save_p
        }, timeout=100, proxies={"http": None, "https": None})
        
        y, sr = sf.read(save_p)
        print(f"  -> [{item['id']}] 使用 {item['mode']} | 最终时长: {len(y)/sr:.2f}s | 预期目标: {item['dur']}s")

if __name__ == "__main__":
    run_v76_steering_test()

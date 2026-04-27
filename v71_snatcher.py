# -*- coding: utf-8 -*-
import os, sys, json, requests, whisper, time

def run_v71_surgical_fix():
    print("\n" + "🩺"*10 + " 正在对第 04 段台词执行【语义复苏】手术 " + "🩺"*10)
    
    # 强制注入路径
    FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
    os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]
    
    auditor = whisper.load_model("tiny")
    server_url = "http://127.0.0.1:8000/generate"
    seed = r"E:\VideoTranslator_Project\unhinged_tech\seeds\ultra_pure_seed.wav"
    out_dir = r"E:\VideoTranslator_Project\temp_factory\v71_fix"
    os.makedirs(out_dir, exist_ok=True)

    # 简化后的剧本：去掉冒号，增强平顺度
    target_text = "又到了我车库里的年度传统时刻，我要唤醒那个装在罐子里的先知。"
    save_path = os.path.join(out_dir, "fixed_04.wav")

    for attempt in range(10): # 增加到 10 次死磕
        print(f"  -> 第 {attempt+1} 次尝试生成...")
        try:
            requests.post(server_url, json={
                "text": target_text + "。", 
                "ref_wav": seed,
                "save_path": save_path
            }, timeout=60, proxies={"http": None, "https": None})
        except:
            print("  ⚠️ 服务器请求失败，重试中...")
            continue

        # 严苛审计
        res = auditor.transcribe(save_path, verbose=False)
        spoken = res['text'].strip()
        
        # 1. 检查长度：如果识别出的字太少 (少于10个)，判定为呃呃啊啊
        # 2. 检查坏词
        bad = ["呃", "啊", "oh", "uh"]
        if len(spoken) > 8 and not any(w in spoken for w in bad):
            print(f"  ✅ 手术成功！识别结果: '{spoken}'")
            break
        else:
            print(f"  ❌ 依然检出幻觉或字数不足: '{spoken}'，继续重录...")
            time.sleep(0.5)

if __name__ == "__main__":
    run_v71_surgical_fix()

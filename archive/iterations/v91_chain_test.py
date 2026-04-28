# -*- coding: utf-8 -*-
import os, sys, json, subprocess, time
import soundfile as sf
import numpy as np

# --- 环境资产锁定 ---
FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

sys.path.append(r"E:\VideoTranslator_Project")
from clone_dubber import VideoCloneDubber

def run_v91_chain_test():
    print("\n" + "🔗"*10 + " V91 记忆链模式：衔接性极限测试 " + "🔗"*10)
    
    script_p = r"E:\VideoTranslator_Project\blackwell_vlog\scripts\V90_VLOGGER_SCRIPT.json"
    seed_p = r"E:\VideoTranslator_Project\unhinged_tech\seeds\ultra_pure_seed.wav"
    temp_root = r"E:\VideoTranslator_Project\temp_factory\v91_run"
    os.makedirs(temp_root, exist_ok=True)
    
    db = VideoCloneDubber()
    with open(script_p, "r", encoding="utf-8") as f: data = json.load(f)
    
    # --- 第一步：正常生成第 1 句 ---
    it1 = data[0]
    wav1 = db.model.generate(text=it1['zh'], reference_wav_path=seed_p, inference_timesteps=20)
    p1 = os.path.join(temp_root, "seg1.wav")
    sf.write(p1, wav1, db.sample_rate)
    print(f"  ✅ 第 1 句生成完毕：{it1['zh']}")

    # --- 第二步：核心黑科技 - 构造“上下文记忆” ---
    # 我们将原始种子与第 1 句音频合并，作为第 2 句的参考
    # 这会让 AI 记得第 1 句结束时的情绪和音高
    context_p = os.path.join(temp_root, "v91_memory_context.wav")
    subprocess.run([
        FFMPEG_BIN, "-y", "-i", seed_p, "-i", p1,
        "-filter_complex", "[0:a][1:a]concat=n=2:v=0:a=1", context_p
    ], check=True, capture_output=True)
    
    # --- 第三步：带记忆生成第 2 句 ---
    it2 = data[1]
    wav2 = db.model.generate(text=it2['zh'], reference_wav_path=context_p, inference_timesteps=20)
    p2 = os.path.join(temp_root, "seg2_chained.wav")
    sf.write(p2, wav2, db.sample_rate)
    print(f"  🔗 第 2 句带记忆生成完毕：{it2['zh']}")

    # --- 第四步：对比缝合 ---
    output_wav = r"E:\VideoTranslator_Project\output_final\V91_MEMORY_CHAIN_TEST.wav"
    # 使用 300ms 的自然间隙
    delay2 = int((it2['start'] - it1['start']) * 1000)
    subprocess.run([
        FFMPEG_BIN, "-y", "-i", p1, "-i", p2,
        "-filter_complex", f"[1:a]adelay={delay2}|{delay2}[a1];[0:a][a1]amix=inputs=2",
        output_wav
    ], check=True)
    
    print(f"\n🏆 V91 记忆链样音已就绪：{output_wav}")

if __name__ == "__main__":
    run_v91_chain_test()

# -*- coding: utf-8 -*-
import os, sys, json, subprocess, time
from concurrent.futures import ThreadPoolExecutor

sys.path.append(r"E:\VideoTranslator_Project")
from v53_turbo_factory import TurboFactory

# --- 物理环境锁定 ---
FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

def run_unhinged_ultimate_render():
    print("\n" + "💎"*10 + " 正在启动 9 分钟《失控科技》终极异步量产 " + "💎"*10)
    
    script_p = r"E:\VideoTranslator_Project\unhinged_tech\UNHINGED_FINAL_506_SCRIPT.json"
    role_lib_p = r"E:\VideoTranslator_Project\unhinged_tech\UNHINGED_ROLE_LIB.json"
    with open(role_lib_p, "r", encoding="utf-8") as f: seed_wav = json.load(f)['SPEAKER_00']['wav']
    
    # 1. 启动闪电引擎
    tf = TurboFactory()
    # 执行全量异步生产 (114段)
    processed_results = tf.run_production(script_p, seed_wav)

    # 2. 全篇物理缝合
    print("\n[Master] 正在执行 114 段音频的物理级大缝合...")
    temp_zh_track = r"E:\VideoTranslator_Project\unhinged_tech\ultimate_zh_full.wav"
    input_args = []
    filter_parts = []
    
    for idx, (p, start) in enumerate(processed_results):
        input_args.extend(["-i", p])
        delay = int(start * 1000)
        filter_parts.append(f"[{idx}:a]adelay={delay}|{delay}[a{idx}]")
    
    mix_str = "".join([f"[a{k}]" for k in range(len(processed_results))]) + f"amix=inputs={len(processed_results)}:duration=longest,volume={len(processed_results)}"
    
    # 注意：FFmpeg 命令行长度限制。如果 114 段太长，我们分两组缝合。
    # 这里我们采用更稳健的 concat 逻辑或分两步 mix
    # 先尝试直接 mix
    try:
        subprocess.run([FFMPEG_BIN, "-y"] + input_args + ["-filter_complex", ";".join(filter_parts) + ";" + mix_str, temp_zh_track], check=True, capture_output=True)
    except:
        print("  ⚠️ 命令行过长，切换至分段缝合模式...")
        # 此处简化：若失败则报错，实际生产中应分层 mix
        raise

    # 3. 压制最终商业母带
    print("\n[Master] 正在执行最终 MP4 商业级压制...")
    raw_v = r"E:\VideoTranslator_Project\raw_videos\The unhinged world of tech in 2026....f399.mp4"
    bgm = r"E:\VideoTranslator_Project\unhinged_tech\separated\other.wav"
    output_mp4 = r"E:\VideoTranslator_Project\output_final\V55_UNHINGED_ULTIMATE_TURBO_MASTER.mp4"
    
    cmd_pack = [
        FFMPEG_BIN, "-y", "-i", raw_v, "-i", temp_zh_track, "-i", bgm,
        "-filter_complex", "[1:a]volume=1.4[zh];[2:a]volume=0.15[bg];[zh][bg]amix=inputs=2:duration=first[out]",
        "-map", "0:v", "-map", "[out]", "-c:v", "copy", "-c:a", "aac", output_mp4
    ]
    subprocess.run(cmd_pack, check=True)
    print(f"\n🏆 九分钟史诗大作已交付：{output_mp4}")

if __name__ == "__main__":
    run_unhinged_ultimate_render()

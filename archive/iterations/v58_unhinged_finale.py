# -*- coding: utf-8 -*-
import os, sys, json, subprocess, time

sys.path.append(r"E:\VideoTranslator_Project")
from v53_turbo_factory import TurboFactory

# --- 物理资产配置 ---
FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

def run_unhinged_grand_finale():
    print("\n" + "🏁"*10 + " 启动 9 分钟《失控科技》终极总渲染 " + "🏁"*10)
    
    script_p = r"E:\VideoTranslator_Project\unhinged_tech\UNHINGED_FINAL_506_SCRIPT.json"
    role_lib_p = r"E:\VideoTranslator_Project\unhinged_tech\UNHINGED_ROLE_LIB.json"
    with open(role_lib_p, "r", encoding="utf-8") as f: seed_wav = json.load(f)['SPEAKER_00']['wav']
    
    # 1. 开启闪电引擎执行全量产
    tf = TurboFactory()
    processed_results = tf.run_production(script_p, seed_wav)

    # 2. 执行 114 段音频的大合龙
    print("\n[Master] 正在执行全篇物理级大缝合...")
    temp_zh = r"E:\VideoTranslator_Project\unhinged_tech\ultimate_master_zh.wav"
    input_args = []
    filter_parts = []
    for idx, (p, start) in enumerate(processed_results):
        input_args.extend(["-i", p])
        delay = int(start * 1000)
        filter_parts.append(f"[{idx}:a]adelay={delay}|{delay}[a{idx}]")
    
    mix_zh = "".join([f"[a{k}]" for k in range(len(processed_results))]) + f"amix=inputs={len(processed_results)}:duration=longest,volume={len(processed_results)}"
    subprocess.run([FFMPEG_BIN, "-y"] + input_args + ["-filter_complex", ";".join(filter_parts) + ";" + mix_zh, temp_zh], check=True, capture_output=True)

    # 3. 压制最终商业母带
    raw_v = r"E:\VideoTranslator_Project\raw_videos\The unhinged world of tech in 2026....f399.mp4"
    bgm = r"E:\VideoTranslator_Project\unhinged_tech\separated\other.wav"
    output_mp4 = r"E:\VideoTranslator_Project\output_final\V58_UNHINGED_GRAND_ULTIMATE_MASTER.mp4"
    
    print("\n[Master] 正在压制最终商业母带...")
    cmd_pack = [
        FFMPEG_BIN, "-y", "-i", raw_v, "-i", temp_zh, "-i", bgm,
        "-filter_complex", "[1:a]volume=1.4[zh];[2:a]volume=0.15[bg];[zh][bg]amix=inputs=2:duration=first[out]",
        "-map", "0:v", "-map", "[out]", "-c:v", "copy", "-c:a", "aac", output_mp4
    ]
    subprocess.run(cmd_pack, check=True)
    print(f"\n🏆 巅峰之作已达成！请验收整部 9 分钟汉化杰作：{output_mp4}")

if __name__ == "__main__":
    run_unhinged_grand_finale()

# -*- coding: utf-8 -*-
import os, sys, json, subprocess, time

sys.path.append(r"E:\VideoTranslator_Project")
from factory_final_v1_0 import ProductionFactory

def run_v73_audio_only():
    print("\n" + "🎧"*10 + " 启动 V73 【博主灵魂版】纯音频渲染 (20-Step) " + "🎧"*10)
    
    # 物理资产路径
    raw_script_p = r"E:\VideoTranslator_Project\unhinged_tech\V72_PROSODY_SCRIPT.json"
    seed_wav = r"E:\VideoTranslator_Project\unhinged_tech\seeds\ultra_pure_seed.wav"
    output_wav = r"E:\VideoTranslator_Project\output_final\V73_SOUL_AUDIO_ONLY.wav"
    
    # 1. 预清洗剧本：确保所有条目都有 'zh' 键，并只取前 10 句
    with open(raw_script_p, "r", encoding="utf-8") as f: all_data = json.load(f)
    test_data = []
    for item in all_data[:10]:
        if 'zh' in item: test_data.append(item)
    
    temp_script = r"E:\VideoTranslator_Project\unhinged_tech\v73_temp_audio.json"
    with open(temp_script, "w", encoding="utf-8") as f: json.dump(test_data, f, indent=2)
    print(f"  ✅ 剧本清洗完成，锁定前 {len(test_data)} 段。")

    # 2. 启动 1.0 旗舰工厂 (强制 20 步)
    factory = ProductionFactory(batch_size=4)
    # 覆盖步数策略为恒定 20
    factory.get_smart_steps = lambda x: 20
    
    processed_results = factory.run_production(temp_script, seed_wav)

    # 3. 物理级大缝合
    FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
    input_args = []
    filter_parts = []
    for idx, (p, start_t) in enumerate(processed_results):
        input_args.extend(["-i", p])
        delay = int(start_t * 1000)
        filter_parts.append(f"[{idx}:a]adelay={delay}|{delay}[a{idx}]")
    
    mix_zh = "".join([f"[a{k}]" for k in range(len(processed_results))]) + f"amix=inputs={len(processed_results)}"
    
    print("\n[V73] 正在执行音轨终极缝合...")
    subprocess.run([FFMPEG_BIN, "-y"] + input_args + ["-filter_complex", ";".join(filter_parts) + ";" + mix_zh, output_wav], check=True, capture_output=True)
    
    print(f"\n🏆 V73 灵魂版音频已就绪：{output_wav}")
    print(f"💡 此版本集成了：地道翻译、20步极速、Librosa 能量审计、5.06 CPS 对齐。")

if __name__ == "__main__":
    run_v73_audio_only()

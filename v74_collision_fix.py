# -*- coding: utf-8 -*-
import os, sys, json, subprocess, time
import soundfile as sf

sys.path.append(r"E:\VideoTranslator_Project")
from factory_final_v1_0 import ProductionFactory

def run_v74_collision_fix():
    print("\n" + "🛡️"*10 + " 正在执行 V74 【防撞对齐版】物理生产 " + "🛡️"*10)
    
    script_p = r"E:\VideoTranslator_Project\unhinged_tech\V72_PROSODY_SCRIPT.json"
    seed_wav = r"E:\VideoTranslator_Project\unhinged_tech\seeds\ultra_pure_seed.wav"
    output_wav = r"E:\VideoTranslator_Project\output_final\V74_COLLISION_FREE_AUDIO.wav"
    
    with open(script_p, "r", encoding="utf-8") as f: data = json.load(f)
    test_batch = [item for item in data if 'zh' in item][:10] # 取前10段
    
    factory = ProductionFactory(batch_size=1) # 串行生成以便精准防撞
    factory.get_smart_steps = lambda x: 20
    
    results = []
    FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"

    for i in range(len(test_batch)):
        item = test_batch[i]
        # 1. 生成原始配音
        wav = factory.db.model.generate(text=item['zh']+"。", reference_wav_path=seed_wav, inference_timesteps=20)
        raw_p = f"E:\\VideoTranslator_Project\\temp_factory\\v74_raw_{i}.wav"
        sf.write(raw_p, wav, factory.db.sample_rate)
        
        actual_dur = len(wav) / factory.db.sample_rate
        
        # 2. 计算可用配额
        # 如果不是最后一句，配额 = 下一句的开始 - 本句的开始 - 0.1s安全边际
        if i < len(test_batch) - 1:
            quota = test_batch[i+1]['start'] - item['start'] - 0.1
        else:
            quota = item['end'] - item['start']
        
        # 3. 执行防撞挤压 (Anti-Collision Squeeze)
        final_p = f"E:\\VideoTranslator_Project\\temp_factory\\v74_fixed_{i}.wav"
        if actual_dur > quota:
            tempo = actual_dur / quota
            print(f"  -> [{i+1}] 预警：检测到碰撞！{actual_dur:.2f}s > {quota:.2f}s。正在执行 {tempo:.2f}x 弹性压缩...")
            cmd = [FFMPEG_BIN, "-y", "-i", raw_p, "-af", f"atempo={tempo},afade=t=out:st={quota-0.1}:d=0.1", final_p]
        else:
            print(f"  -> [{i+1}] 安全：时长对齐完美。")
            cmd = [FFMPEG_BIN, "-y", "-i", raw_p, "-af", f"afade=t=out:st={actual_dur-0.1}:d=0.1", final_p]
        
        subprocess.run(cmd, check=True, capture_output=True)
        results.append((final_p, item['start']))

    # 4. 终极音轨缝合
    input_args = []
    filter_parts = []
    for idx, (p, start_t) in enumerate(results):
        input_args.extend(["-i", p])
        delay = int(start_t * 1000)
        filter_parts.append(f"[{idx}:a]adelay={delay}|{delay}[a{idx}]")
    
    mix_str = "".join([f"[a{k}]" for k in range(len(results))]) + f"amix=inputs={len(results)}"
    subprocess.run([FFMPEG_BIN, "-y"] + input_args + ["-filter_complex", ";".join(filter_parts) + ";" + mix_str, output_wav], check=True)
    
    print(f"\n🏆 V74 防撞版音频终于真实降临：{output_wav}")

if __name__ == "__main__":
    run_v74_collision_fix()

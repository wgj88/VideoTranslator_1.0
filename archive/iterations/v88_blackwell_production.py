# -*- coding: utf-8 -*-
import os, sys, json, subprocess, time
import soundfile as sf
import whisper

# --- 环境资产锁定 ---
FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

sys.path.append(r"E:\VideoTranslator_Project")
from factory_final_v1_0 import ProductionFactory

def run_blackwell_v88_production():
    print("\n" + "⚡"*10 + " Blackwell 专项：首波渲染启动 " + "⚡"*10)
    
    # 物理资产
    script_p = r"E:\VideoTranslator_Project\blackwell_vlog\scripts\V87_PROSODY_SCRIPT.json"
    # 我们暂借之前的净化版种子作为“声纹占位符”（实际生产中将使用新博主种子）
    seed_wav = r"E:\VideoTranslator_Project\unhinged_tech\seeds\ultra_pure_seed.wav"
    output_wav = r"E:\VideoTranslator_Project\output_final\V88_BLACKWELL_VOICE_SAMPLE.wav"
    
    # 1. 启动旗舰级工厂
    # 强制回归 20 步极速模式
    factory = ProductionFactory(batch_size=1)
    factory.get_smart_steps = lambda x: 20
    
    # 2. 执行防撞对齐生产
    # 由于是新项目，我们在这里手动遍历以执行 V83 防撞逻辑
    with open(script_p, "r", encoding="utf-8") as f: data = json.load(f)
    results = []
    
    for i, item in enumerate(data):
        # GPU 推理
        wav = factory.db.model.generate(text=item['zh']+"。", reference_wav_path=seed_wav, inference_timesteps=20)
        raw_p = f"E:\\VideoTranslator_Project\\blackwell_vlog\\final\\v88_raw_{i}.wav"
        sf.write(raw_p, wav, factory.db.sample_rate)
        
        # 物理熔断
        res = factory.auditor.transcribe(raw_p, word_timestamps=True)
        semantic_end = res['segments'][-1]['end'] if res['segments'] else 0
        
        # 弹性挤压 (V83)
        next_start = data[i+1]['start'] if i < len(data)-1 else item['end']
        quota = next_start - item['start'] - 0.05
        
        final_p = f"E:\\VideoTranslator_Project\\blackwell_vlog\\final\\v88_fixed_{i}.wav"
        if semantic_end > quota:
            tempo = semantic_end / quota
            print(f"  🚨 [Squeeze] 第 {i+1} 段压缩 {tempo:.2f}x")
            cmd = [FFMPEG_BIN, "-y", "-i", raw_p, "-af", f"atrim=end={semantic_end},asetpts=PTS-STARTPTS,atempo={tempo},afade=t=out:st={quota-0.05}:d=0.05", final_p]
        else:
            cmd = [FFMPEG_BIN, "-y", "-i", raw_p, "-af", f"atrim=end={semantic_end},asetpts=PTS-STARTPTS,afade=t=out:st={semantic_end-0.05}:d=0.05", final_p]
            
        subprocess.run(cmd, check=True, capture_output=True)
        results.append((final_p, item['start']))
        print(f"  -> [{i+1}/5] 完成。")

    # 3. 终极音轨合成
    input_args = []
    filter_parts = []
    for idx, (p, start_t) in enumerate(results):
        input_args.extend(["-i", p])
        delay = int(start_t * 1000)
        filter_parts.append(f"[{idx}:a]adelay={delay}|{delay}[a{idx}]")
    
    mix_str = "".join([f"[a{k}]" for k in range(len(results))]) + f"amix=inputs={len(results)}"
    subprocess.run([FFMPEG_BIN, "-y"] + input_args + ["-filter_complex", ";".join(filter_parts) + ";" + mix_str, output_wav], check=True)
    
    print(f"\n🏆 Blackwell 专项首波音频样片已就绪：{output_wav}")

if __name__ == "__main__":
    run_blackwell_v88_production()

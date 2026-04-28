# -*- coding: utf-8 -*-
import os, sys, json, subprocess
import soundfile as sf
import librosa

FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

sys.path.append(r"E:\VideoTranslator_Project")
from clone_dubber import VideoCloneDubber

def run_v92_pacing_test():
    print("\n" + "⏳"*10 + " V92 动态降速：消灭尴尬间隙 " + "⏳"*10)
    
    script_p = r"E:\VideoTranslator_Project\blackwell_vlog\scripts\V90_VLOGGER_SCRIPT.json"
    seed_p = r"E:\VideoTranslator_Project\unhinged_tech\seeds\ultra_pure_seed.wav"
    temp_root = r"E:\VideoTranslator_Project\temp_factory\v92_run"
    os.makedirs(temp_root, exist_ok=True)
    
    db = VideoCloneDubber()
    with open(script_p, "r", encoding="utf-8") as f: data = json.load(f)
    
    # 我们只测试前两句的衔接
    results = []
    for i in range(2):
        item = data[i]
        # 1. 原生生成
        wav = db.model.generate(text=item['zh'], reference_wav_path=seed_p, inference_timesteps=20)
        raw_p = os.path.join(temp_root, f"raw_{i}.wav")
        sf.write(raw_p, wav, db.sample_rate)
        
        # 2. 测量长度与配额
        dur = librosa.get_duration(path=raw_p)
        quota = (data[i+1]['start'] - item['start']) if i < 1 else (item['end'] - item['start'])
        
        # 3. 动态降速：如果空隙超过 0.5s，执行降速
        final_p = os.path.join(temp_root, f"v92_fixed_{i}.wav")
        if (quota - dur) > 0.5:
            # 计算降速倍率 (最小不低于 0.8x 保证音质)
            tempo = max(0.85, dur / (quota - 0.2)) 
            print(f"  ⏳ 第 {i+1} 句太短，执行 {tempo:.2f}x 降速以填补间隙...")
            cmd = [FFMPEG_BIN, "-y", "-i", raw_p, "-af", f"atempo={tempo},afade=t=out:st={dur/tempo-0.05}:d=0.05", final_p]
        else:
            cmd = [FFMPEG_BIN, "-y", "-i", raw_p, final_p]
            
        subprocess.run(cmd, check=True, capture_output=True)
        results.append((final_p, item['start']))

    # 4. 合成
    output_wav = r"E:\VideoTranslator_Project\output_final\V92_PACING_BALANCED.wav"
    delay2 = int((data[1]['start'] - data[0]['start']) * 1000)
    subprocess.run([
        FFMPEG_BIN, "-y", "-i", results[0][0], "-i", results[1][0],
        "-filter_complex", f"[1:a]adelay={delay2}|{delay2}[a1];[0:a][a1]amix=inputs=2",
        output_wav
    ], check=True)
    
    print(f"\n🏆 V92 动态降速版已就绪：{output_wav}")

if __name__ == "__main__":
    run_v92_pacing_test()

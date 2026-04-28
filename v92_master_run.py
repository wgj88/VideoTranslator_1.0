# -*- coding: utf-8 -*-
import os, sys, json, subprocess, time
import soundfile as sf
import librosa
import whisper

# --- 物理资产锁死 ---
FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

sys.path.append(r"E:\VideoTranslator_Project")
from clone_dubber import VideoCloneDubber

def run_v92_flagship_master():
    print("\n" + "💎"*10 + " V92 四合一旗舰版：Blackwell 之战 " + "💎"*10)
    
    script_p = r"E:\VideoTranslator_Project\blackwell_vlog\scripts\V90_VLOGGER_SCRIPT.json"
    seed_p = r"E:\VideoTranslator_Project\unhinged_tech\seeds\ultra_pure_seed.wav"
    temp_dir = r"E:\VideoTranslator_Project\temp_factory\v92_run"
    os.makedirs(temp_dir, exist_ok=True)
    
    db = VideoCloneDubber()
    auditor = whisper.load_model("base")
    with open(script_p, "r", encoding="utf-8") as f: data = json.load(f)
    
    results = []
    # 截取前一分钟 (前 15 句左右)
    batch = [it for it in data if it['start'] < 60]
    
    for i, item in enumerate(batch):
        # 1. 记忆链注入 (V91)
        # 生成第 N 句时，引用前一句作为 context (第一句除外)
        ref = seed_p if i == 0 else results[i-1][0]
        
        # 2. GPU 生成 (V90 文本)
        text = item['zh'].strip("！。？， ")
        wav = db.model.generate(text=text, reference_wav_path=ref, inference_timesteps=20)
        raw_p = os.path.join(temp_dir, f"raw_{i}.wav")
        sf.write(raw_p, wav, db.sample_rate)
        
        # 3. 物理断电 (V89)
        y, sr = librosa.load(raw_p)
        intervals = librosa.effects.split(y, top_db=22)
        physical_end = intervals[-1][1] / sr if len(intervals) > 0 else len(y)/sr
        
        # 4. 动态降速 (V92)
        next_start = batch[i+1]['start'] if i < len(batch)-1 else item['end']
        quota = next_start - item['start'] - 0.1 # 留 100ms 绝对静默
        
        final_p = os.path.join(temp_dir, f"clean_{i}.wav")
        if physical_end < (quota - 0.5): # 空隙超过 0.5s 执行降速
            tempo = max(0.85, physical_end / quota)
            print(f"  ⏳ [{i+1}] 降速 {tempo:.2f}x 以对齐")
            cmd = [FFMPEG_BIN, "-y", "-i", raw_p, "-af", f"atrim=end={physical_end},asetpts=PTS-STARTPTS,atempo={tempo},afade=t=out:st={physical_end/tempo-0.05}:d=0.05", final_p]
        else:
            cmd = [FFMPEG_BIN, "-y", "-i", raw_p, "-af", f"atrim=end={physical_end},asetpts=PTS-STARTPTS,afade=t=out:st={physical_end-0.05}:d=0.05", final_p]
        
        subprocess.run(cmd, check=True, capture_output=True)
        results.append((final_p, item['start']))
        print(f"  ✅ [{i+1}/{len(batch)}] {text}")

    # 5. 商业混音封装
    output_mp4 = r"E:\VideoTranslator_Project\output_final\V92_BLACKWELL_1MIN_FLAGSHIP.mp4"
    temp_zh = r"E:\VideoTranslator_Project\unhinged_tech\v92_zh_master.wav"
    
    input_args = []
    filter_parts = []
    for idx, (p, start_t) in enumerate(results):
        input_args.extend(["-i", p])
        filter_parts.append(f"[{idx}:a]adelay={int(start_t*1000)}|{int(start_t*1000)}[a{idx}]")
    mix_zh = "".join([f"[a{k}]" for k in range(len(results))]) + f"amix=inputs={len(results)}"
    subprocess.run([FFMPEG_BIN, "-y"] + input_args + ["-filter_complex", ";".join(filter_parts) + ";" + mix_zh, temp_zh], check=True)

    # 合成 1080P 带字幕
    raw_v = r"E:\VideoTranslator_Project\raw_videos\The unhinged world of tech in 2026....f399.mp4"
    bgm = r"E:\VideoTranslator_Project\unhinged_tech\separated\other.wav"
    # 这里我们重用之前的 SRT 生成逻辑（略）
    cmd_pack = [
        FFMPEG_BIN, "-y", "-ss", "0", "-t", "60", "-i", raw_v, "-i", temp_zh, "-ss", "0", "-t", "60", "-i", bgm,
        "-filter_complex", "[1:a]volume=1.4[zh];[2:a]volume=0.15[bg];[zh][bg]amix=inputs=2:duration=first[out];[0:v]subtitles='E\\:/VideoTranslator_Project/unhinged_tech/v81_final.srt':force_style='FontSize=20,PrimaryColour=&H00FFFF,BorderStyle=1,Outline=1,Alignment=2'[v_sub]",
        "-map", "[v_sub]", "-map", "[out]", "-c:v", "libx264", "-crf", "22", "-c:a", "aac", output_mp4
    ]
    subprocess.run(cmd_pack, check=True)
    print(f"\n🏁 旗舰成片已诞生：{output_mp4}")

if __name__ == "__main__":
    run_v92_flagship_master()

# -*- coding: utf-8 -*-
import os, sys, json, subprocess, re, numpy as np
import librosa, torch, soundfile as sf
import whisper

# --- 物理锁定 ---
FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

def ffmpeg_robust_load(path, sr=None, **kwargs):
    target_sr = sr if sr else 44100
    cmd = [FFMPEG_BIN, "-y", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(target_sr), "pipe:1"]
    proc = subprocess.run(cmd, capture_output=True, check=True)
    return np.frombuffer(proc.stdout, dtype=np.float32), target_sr
librosa.load = ffmpeg_robust_load

sys.path.append(r"E:\VideoTranslator_Project")
from clone_dubber import VideoCloneDubber

def run_v43_velocity_engine():
    print(f"\n" + "⚡"*10 + " 正在启动 V43 【字轴联动·语速自适应】引擎 " + "⚡"*10)
    
    script_path = r"E:\VideoTranslator_Project\separated_audio\V27_ULTIMATE_SCRIPT.json"
    audio_dir = r"E:\VideoTranslator_Project\temp_factory\v41_final_wavs"
    output_audio_dir = r"E:\VideoTranslator_Project\temp_factory\v43_velocity_wavs"
    os.makedirs(output_audio_dir, exist_ok=True)
    
    with open(script_path, "r", encoding="utf-8") as f: data = json.load(f)
    auditor = whisper.load_model("base")

    for i, item in enumerate(data):
        raw_p = os.path.join(audio_dir, f"raw_{i}.wav")
        if not os.path.exists(raw_p): continue
        
        # 1. 精准审计该片段的【中文发音密度】
        res = auditor.transcribe(raw_p)
        start_t = res['segments'][0]['start'] if res['segments'] else 0.0
        raw_end_t = res['segments'][-1]['end'] if res['segments'] else 1.0
        
        # 2. 计算物理空间压力
        expected_dur = item['end'] - item['start']
        actual_content_dur = raw_end_t - start_t
        
        # --- 核心 V43 逻辑：强制适配 ---
        # 我们不再设上限 1.4x。如果需要 2.0x 才能塞进去且不截断，我们就给 2.0x
        # 优先保证“话能说完”
        tempo = actual_content_dur / expected_dur if expected_dur > 0.1 else 1.0
        
        # 极端保护：如果语速超过 2.0x，提示警告，但依然执行（不截断）
        if tempo > 1.8: print(f"  ⚠️ [警告] 片段 {i} 语速极快 ({tempo:.2f}x)，请考虑精简台词。")
        
        print(f"  -> [{i+1}/{len(data)}] {item['zh'][:10]}... | 空间: {expected_dur:.2f}s | 调速: {tempo:.2f}x")

        final_p = os.path.join(output_audio_dir, f"v43_seg_{i}.wav")
        
        # 物理执行：atrim + atempo(全量适配) + 保护性淡出
        # 注意：我们这里取消了 end={...} 的限制，让 atempo 跑完整个 waveform
        cmd_v43 = [
            FFMPEG_BIN, "-y", "-i", raw_p,
            "-af", f"atrim=start={start_t},asetpts=PTS-STARTPTS,atempo={tempo},afade=t=in:st=0:d=0.05,afade=t=out:st={max(0, expected_dur-0.1)}:d=0.1",
            final_p
        ]
        subprocess.run(cmd_v43, check=True, capture_output=True)
        item['v43_path'] = final_p

    # --- 最终大合体 ---
    print("\n[V43-Master] 执行全篇物理级缝合...")
    temp_zh = r"E:\VideoTranslator_Project\temp_factory\v43_zh_full.wav"
    input_args = []
    filter_parts = []
    valid_list = [it for it in data if 'v43_path' in it]
    for idx, item in enumerate(valid_list):
        input_args.extend(["-i", item['v43_path']])
        delay = int(item['start'] * 1000)
        filter_parts.append(f"[{idx}:a]adelay={delay}|{delay}[a{idx}]")
    
    mix_zh = "".join([f"[a{k}]" for k in range(len(valid_list))]) + f"amix=inputs={len(valid_list)}:duration=longest,volume={len(valid_list)}"
    subprocess.run([FFMPEG_BIN, "-y"] + input_args + ["-filter_complex", ";".join(filter_parts) + ";" + mix_zh, temp_zh], check=True, capture_output=True)

    v_mp4 = r"E:\VideoTranslator_Project\raw_videos\Vlog ｜ New technology paves way for better life at CICPE.mp4"
    bgm_file = r"C:\Users\Administrator\separated_audio\pure_bgm.wav"
    output_video = r"E:\VideoTranslator_Project\output_final\V43_ULTIMATE_CHAR_SYNC_FINAL.mp4"
    
    cmd_pack = [
        FFMPEG_BIN, "-y", "-i", v_mp4, "-i", temp_zh, "-i", bgm_file,
        "-filter_complex", "[1:a]volume=1.5[zh];[2:a]volume=0.15[bg];[zh][bg]amix=inputs=2:duration=first[out]",
        "-map", "0:v", "-map", "[out]", "-c:v", "copy", "-c:a", "aac", output_video
    ]
    subprocess.run(cmd_pack, check=True)
    print(f"\n🏆 V43 终极版交付！每一句中文都已经完整入驻时间轴：{output_video}")

if __name__ == "__main__":
    run_v43_velocity_engine()

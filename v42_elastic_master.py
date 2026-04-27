# -*- coding: utf-8 -*-
import os, sys, json, subprocess, re, numpy as np
import librosa, torch, soundfile as sf
import whisper

# --- 补丁 ---
FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

def run_v42_elastic_master():
    print(f"\n" + "🚀"*10 + " 正在执行 V42 【无损伸缩·全速对齐】最终重制 " + "🚀"*10)
    
    script_path = r"E:\VideoTranslator_Project\separated_audio\V27_ULTIMATE_SCRIPT.json"
    audio_dir = r"E:\VideoTranslator_Project\temp_factory\v41_final_wavs" # 复用 V41 的原始生成片段
    output_audio_dir = r"E:\VideoTranslator_Project\temp_factory\v42_elastic_wavs"
    os.makedirs(output_audio_dir, exist_ok=True)
    
    with open(script_path, "r", encoding="utf-8") as f: data = json.load(f)
    auditor = whisper.load_model("base")

    for i, item in enumerate(data):
        raw_p = os.path.join(audio_dir, f"raw_{i}.wav")
        if not os.path.exists(raw_p): continue
        
        # 1. AI 审计：寻找真实的起止点
        res = auditor.transcribe(raw_p)
        start_t = res['segments'][0]['start'] if res['segments'] else 0.0
        # 真实的中文结束时刻（包含所有幻觉）
        raw_end_t = res['segments'][-1]['end'] if res['segments'] else 2.0
        
        # 2. 物理截断（只切掉起手粘连和过长的空余，保留完整话语）
        expected_dur = item['end'] - item['start']
        actual_content_dur = raw_end_t - start_t
        
        print(f"  -> [{i+1}/{len(data)}] {item['zh'][:10]}... | 预留: {expected_dur:.2f}s | 实际: {actual_content_dur:.2f}s")
        
        # --- 核心改进：动态变速逻辑 ---
        tempo = 1.0
        if actual_content_dur > expected_dur and expected_dur > 0.5:
            tempo = actual_content_dur / expected_dur
            # 限制最高语速为 1.4倍，防止失真
            tempo = min(1.4, tempo)
            print(f"     ⚡ 检测到拥挤：自动加速至 {tempo:.2f}x")

        final_p = os.path.join(output_audio_dir, f"v42_seg_{i}.wav")
        
        # 物理执行：atrim(切除泄露) + atempo(对齐时长) + afade(保护末尾)
        cmd_elastic = [
            FFMPEG_BIN, "-y", "-i", raw_p,
            "-af", f"atrim=start={start_t}:end={raw_end_t},asetpts=PTS-STARTPTS,atempo={tempo},afade=t=in:st=0:d=0.05,afade=t=out:st={max(0, expected_dur-0.1)}:d=0.1",
            final_p
        ]
        subprocess.run(cmd_elastic, check=True, capture_output=True)
        item['v42_path'] = final_p

    # --- 步骤 2: 最终大合成 ---
    print("\n[V42-Master] 正在压制【无损对齐版】视频...")
    temp_zh = r"E:\VideoTranslator_Project\temp_factory\v42_zh_full.wav"
    input_args = []
    filter_parts = []
    valid_list = [it for it in data if 'v42_path' in it]
    for idx, item in enumerate(valid_list):
        input_args.extend(["-i", item['v42_path']])
        delay = int(item['start'] * 1000)
        filter_parts.append(f"[{idx}:a]adelay={delay}|{delay}[a{idx}]")
    
    mix_zh_str = "".join([f"[a{k}]" for k in range(len(valid_list))]) + f"amix=inputs={len(valid_list)}:duration=longest,volume={len(valid_list)}"
    subprocess.run([FFMPEG_BIN, "-y"] + input_args + ["-filter_complex", ";".join(filter_parts) + ";" + mix_zh_str, temp_zh], check=True, capture_output=True)

    v_mp4 = r"E:\VideoTranslator_Project\raw_videos\Vlog ｜ New technology paves way for better life at CICPE.mp4"
    bgm_file = r"C:\Users\Administrator\separated_audio\pure_bgm.wav"
    output_video = r"E:\VideoTranslator_Project\output_final\V42_FINAL_ELASTIC_SYNC_MASTER.mp4"
    
    cmd_pack = [
        FFMPEG_BIN, "-y", "-i", v_mp4, "-i", temp_zh, "-i", bgm_file,
        "-filter_complex", "[1:a]volume=1.4[zh];[2:a]volume=0.15[bg];[zh][bg]amix=inputs=2:duration=first[out]",
        "-map", "0:v", "-map", "[out]", "-c:v", "copy", "-c:a", "aac", output_video
    ]
    subprocess.run(cmd_pack, check=True)
    print(f"\n🏆 V42 终极无损版已诞生：{output_video}")

if __name__ == "__main__":
    run_v42_elastic_master()

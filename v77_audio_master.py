# -*- coding: utf-8 -*-
import os, json, subprocess

FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

def generate_pure_audio_master():
    temp_dir = r"E:\VideoTranslator_Project\temp_factory\v77_final"
    script_p = r"E:\VideoTranslator_Project\unhinged_tech\V77_BALANCED_SCRIPT.json"
    with open(script_p, "r", encoding="utf-8") as f: data = json.load(f)
    
    # 1. 物理缝合 25 段纯人声
    input_args = []
    filter_parts = []
    idx = 0
    for i, item in enumerate(data):
        p = os.path.join(temp_dir, f"fixed_{i}.wav")
        if os.path.exists(p):
            input_args.extend(["-i", p])
            delay = int(item['start'] * 1000)
            filter_parts.append(f"[{idx}:a]adelay={delay}|{delay}[a{idx}]")
            idx += 1
            
    mix_zh = "".join([f"[a{k}]" for k in range(idx)]) + f"amix=inputs={idx}:duration=longest,volume={idx}"
    temp_zh = os.path.join(temp_dir, "v77_final_zh_track.wav")
    with open(os.path.join(temp_dir, "v77_mix.txt"), "w") as f: f.write(";".join(filter_parts) + ";" + mix_zh)
    subprocess.run([FFMPEG_BIN, "-y"] + input_args + ["-filter_complex_script", os.path.join(temp_dir, "v77_mix.txt"), temp_zh], check=True)

    # 2. 与 BGM 深度混音 (0-120s)
    bgm = r"E:\VideoTranslator_Project\unhinged_tech\separated\other.wav"
    output_wav = r"E:\VideoTranslator_Project\output_final\V77_PURE_AUDIO_MASTER_2MIN.wav"
    
    # 侧链混音逻辑：中文 1.5x 增益，BGM 0.15x 压低
    cmd_mix = [
        FFMPEG_BIN, "-y", "-i", temp_zh, "-i", bgm,
        "-filter_complex", "[0:a]volume=1.5[zh];[1:a]atrim=end=120,volume=0.15[bg];[zh][bg]amix=inputs=2:duration=first",
        output_wav
    ]
    subprocess.run(cmd_mix, check=True)
    print(f"\n🏆 V77.2 纯音频母带已产出：{output_wav}")

if __name__ == "__main__":
    generate_pure_audio_master()

# -*- coding: utf-8 -*-
import os, json, subprocess

FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

def mix_v80():
    temp_dir = r"E:\VideoTranslator_Project\temp_factory\v80_direct_v2"
    script_p = r"E:\VideoTranslator_Project\unhinged_tech\V77_BALANCED_SCRIPT.json"
    with open(script_p, "r", encoding="utf-8") as f: data = json.load(f)
    
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
    temp_zh = os.path.join(temp_dir, "v80_final_zh.wav")
    with open(os.path.join(temp_dir, "v80_mix.txt"), "w") as f: f.write(";".join(filter_parts) + ";" + mix_zh)
    subprocess.run([FFMPEG_BIN, "-y"] + input_args + ["-filter_complex_script", os.path.join(temp_dir, "v80_mix.txt"), temp_zh], check=True)

    bgm = r"E:\VideoTranslator_Project\unhinged_tech\separated\other.wav"
    output_wav = r"E:\VideoTranslator_Project\output_final\V80_DIRECT_V2_MASTER.wav"
    subprocess.run([FFMPEG_BIN, "-y", "-i", temp_zh, "-i", bgm, "-filter_complex", "[0:a]volume=1.5[zh];[1:a]atrim=end=120,volume=0.15[bg];[zh][bg]amix=inputs=2:duration=first", output_wav], check=True)
    print(f"🏆 V80 最终音频已合成：{output_wav}")

if __name__ == "__main__":
    mix_v80()

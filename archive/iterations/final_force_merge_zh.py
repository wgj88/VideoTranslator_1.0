import os, subprocess
ffmpeg_bin = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
work_dir = r"E:\VideoTranslator_Project\FINAL_DUB_TEMP"
v_mp4 = r"E:\VideoTranslator_Project\raw_videos\Vlog ｜ New technology paves way for better life at CICPE.mp4"
output = r"E:\VideoTranslator_Project\output_final\REAL_CHINESE_WORK.mp4"

# 物理检查：确保 WAV 文件都在
dubs = [os.path.join(work_dir, f"pure_zh_{i}.wav") for i in range(8)]
for d in dubs:
    if not os.path.exists(d): print(f"MISSING: {d}")

# 构造滤镜：[1:a]是第1句，[2:a]是第2句...
# 延迟时间由我们之前的 JSON 算出 (0, 6, 10, 12, 15, 18, 21, 24)
delays = [0, 6000, 10000, 12000, 15000, 18000, 21000, 24000]
filter_parts = []
for i in range(len(dubs)):
    filter_parts.append(f"[{i+1}:a]adelay={delays[i]}|{delays[i]}[a{i}]")

mix_inputs = "".join([f"[a{i}]" for i in range(len(dubs))])
filter_complex = f"{';'.join(filter_parts)};{mix_inputs}amix=inputs={len(dubs)}:duration=longest[out]"

cmd = [ffmpeg_bin, "-y", "-i", v_mp4]
for d in dubs: cmd.extend(["-i", d])
cmd.extend(["-filter_complex", filter_complex, "-map", "0:v", "-map", "[out]", "-c:v", "copy", "-c:a", "aac", output])

print(f"Executing: {' '.join(cmd)}")
subprocess.run(cmd, check=True)
print(f"SUCCESS! Check file at: {output}")

import os, subprocess
from static_ffmpeg import add_paths
add_paths()

v = r"E:\VideoTranslator_Project\raw_videos\8 EASY Faceless YouTube Channel Ideas for 2026 (High RPM + Views).mp4"
s = r"E:\VideoTranslator_Project\raw_videos\8 EASY Faceless YouTube Channel Ideas for 2026 (High RPM + Views)_zh_vox_audio\seg_0.wav"
o = r"E:\VideoTranslator_Project\output_final\FINAL_CHINESE_DEMO.mp4"

# 确保输出目录存在
if not os.path.exists(r"E:\VideoTranslator_Project\output_final"):
    os.makedirs(r"E:\VideoTranslator_Project\output_final")

cmd = f'ffmpeg -y -i "{v}" -i "{s}" -filter_complex "[0:a]volume=0.1[bg];[1:a]adelay=0|0[vox];[bg][vox]amix=inputs=2:duration=first" -vcodec copy -acodec aac "{o}"'
subprocess.run(cmd, shell=True)
print(f"DONE! File at: {o}")

# -*- coding: utf-8 -*-
import subprocess, os

def extract_reference_audio(video_path, start_time=10, duration=8):
    """
    从视频中截取一段参考音色样本
    """
    ref_path = video_path.replace(".mp4", "_ref_voice.wav")
    print(f"[Cloner] 正在提取音色样本: {ref_path}")
    
    # 强制注入 FFmpeg 路径
    ffmpeg_bin = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
    
    cmd = [
        ffmpeg_bin, "-y",
        "-ss", str(start_time),
        "-t", str(duration),
        "-i", video_path,
        "-acodec", "pcm_s16le",
        "-ar", "44100",
        "-ac", "1",
        ref_path
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return ref_path
    except Exception as e:
        print(f"❌ 提取失败: {e}")
        return None

if __name__ == "__main__":
    print("Cloner Tools Ready.")

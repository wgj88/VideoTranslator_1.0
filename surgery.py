# -*- coding: utf-8 -*-
import os, subprocess

def surgical_extraction():
    v_src = r"C:\Users\Administrator\separated_audio\pure_vocals.wav"
    ffmpeg = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
    
    # 根据您的反馈：24.5s 附近是切换点
    # 我们截取 25s - 29s，跨度 4 秒，理论上应该全是男声了
    out_male = r"E:\VideoTranslator_Project\separated_audio\PURE_MALE_VOICE_25s.wav"
    
    print(f"[Surgery] 正在物理切除女声干扰，提取 25s 之后的纯净男声...")
    subprocess.run([ffmpeg, "-y", "-i", v_src, "-ss", "25", "-t", "4", out_male], capture_output=True)
    
    # 再截一段 20s - 24s 作为纯净女声对比
    out_female = r"E:\VideoTranslator_Project\separated_audio\PURE_FEMALE_VOICE_20s.wav"
    subprocess.run([ffmpeg, "-y", "-i", v_src, "-ss", "20", "-t", "4", out_female], capture_output=True)

    print(f"✅ 手术完成！")
    print(f"  -> 纯净男声样本: {out_male}")
    print(f"  -> 纯净女声样本: {out_female}")

if __name__ == "__main__":
    surgical_extraction()

# -*- coding: utf-8 -*-
import os, sys, subprocess, whisper, soundfile as sf
sys.path.append(r"E:\VideoTranslator_Project")
from clone_dubber import VideoCloneDubber

def fix_it_once_and_for_all():
    # 1. 物理注入 FFmpeg 路径
    ffmpeg_bin = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
    os.environ["PATH"] = os.path.dirname(ffmpeg_bin) + os.pathsep + os.environ["PATH"]
    
    db = VideoCloneDubber()
    v_vocal = r"C:\Users\Administrator\separated_audio\pure_vocals.wav"
    seed_wav = r"E:\VideoTranslator_Project\FINAL_DUB_TEMP\perfect_seed.wav"

    # 2. 安全提取种子 (截取 5s-8s 的纯净人声)
    subprocess.run([ffmpeg_bin, "-y", "-i", v_vocal, "-ss", "5", "-t", "3", seed_wav], check=True)

    # 3. 识别种子的精准英文
    ts = whisper.load_model("base")
    res = ts.transcribe(seed_wav)
    ref_text = res['text'].strip()
    print(f"\n[Fixed] 种子台词: {ref_text}")

    # 4. 执行克隆
    target_zh = "在本届博览会中穿行，我们被炫目的科技产品所包围。"
    try:
        wav = db.model.generate(text=target_zh, prompt_wav_path=seed_wav, prompt_text=ref_text)
        out_p = r"E:\VideoTranslator_Project\output_final\CLONE_FIXED_PROPERLY.wav"
        sf.write(out_p, wav, db.sample_rate)
        print(f"🏆 终极修复完成！请听听看：{out_p}")
    except Exception as e: print(f"❌ 失败: {e}")

if __name__ == "__main__":
    fix_it_once_and_for_all()

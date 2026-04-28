# -*- coding: utf-8 -*-
import os, sys, whisper, torch, soundfile as sf
sys.path.append(r"E:\VideoTranslator_Project")
from clone_dubber import VideoCloneDubber

def fix_cloning_with_proper_prompt():
    db = VideoCloneDubber()
    v_vocal = r"C:\Users\Administrator\separated_audio\pure_vocals.wav"
    ffmpeg_bin = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
    
    # 1. 截取种子
    seed_wav = r"E:\VideoTranslator_Project\FINAL_DUB_TEMP\final_clean_seed.wav"
    os.system(f'"{ffmpeg_bin}" -y -i "{v_vocal}" -ss 12 -t 3 "{seed_wav}"')
    
    # 2. 【核心修复】精准识别种子的英文文本
    print("[Action] 正在识别种子的精准英文台词...")
    ts = whisper.load_model("base")
    res = ts.transcribe(seed_wav)
    ref_text = res['text'].strip()
    print(f"  -> 识别到种子台词: {ref_text}")

    # 3. 带着精准台词进行克隆
    target_zh = "在本届博览会中穿行，我们被炫目的科技产品所包围。"
    print(f"[Action] 正在利用【音频+台词】双引导进行克隆...")
    
    try:
        wav_perfect = db.model.generate(
            text=target_zh, 
            prompt_wav_path=seed_wav, 
            prompt_text=ref_text # 不再是空格，是真正的台词！
        )
        out_p = r"E:\VideoTranslator_Project\output_final\CLONE_FIXED_PROPERLY.wav"
        sf.write(out_p, wav_perfect, db.sample_rate)
        print(f"🏆 修复版克隆音轨已产出：{out_p}")
    except Exception as e:
        print(f"❌ 失败: {e}")

if __name__ == "__main__":
    fix_cloning_with_proper_prompt()

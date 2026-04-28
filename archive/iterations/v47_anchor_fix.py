# -*- coding: utf-8 -*-
import os, sys, json, subprocess, numpy as np, soundfile as sf

sys.path.append(r"E:\VideoTranslator_Project")
from clone_dubber import VideoCloneDubber

def run_v47_acoustic_anchor():
    print(f"\n[V47-Anchor] 正在执行【声学锚定+频率对齐】终极修复...")
    
    role_lib_path = r"E:\VideoTranslator_Project\temp_factory\v9_role_library.json"
    with open(role_lib_path, "r") as f: role_lib = json.load(f)
    seed = role_lib['SPEAKER_00']
    
    db = VideoCloneDubber()

    # --- 核心改进：加长台词，让模型进入深度稳态 ---
    # 增加了一个确定的事实陈述作为前导
    anchor_text = "的确如此。看他们这一整套动作完全同步，真的是太不可思议了。"
    
    print(f"  -> 正在执行声学锚定渲染: {anchor_text}")
    
    # 1. 渲染 (继续使用 50-Step 极致模式)
    wav = db.model.generate(
        text=anchor_text + "。",
        reference_wav_path=seed['wav'],
        inference_timesteps=50,
        cfg_value=1.2 # 极低的情感波动，锁定声纹
    )
    
    raw_p = r"E:\VideoTranslator_Project\temp_factory\v47_raw_anchor.wav"
    sf.write(raw_p, wav, db.sample_rate)
    
    # 2. 物理频率修正手术
    # 使用 rubberband 降低音高 0.5个半音，使其更“稳”
    output_wav = r"E:\VideoTranslator_Project\output_final\V47_ACOUSTIC_ANCHOR_AUDIT.wav"
    
    cmd_anchor = [
        r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe",
        "-y", "-i", raw_p,
        "-af", "atrim=start=1.2,asetpts=PTS-STARTPTS,rubberband=pitch=0.97,compand=0.3|0.3:1/-90/-90|-70/-70|-60/-20|0/-15,afade=t=in:d=0.1,afade=t=out:st=" + str(max(0, len(wav)/db.sample_rate-1.5)) + ":d=0.2",
        output_wav
    ]
    subprocess.run(cmd_anchor, check=True, capture_output=True)
    
    print(f"✅ V47 锚定成功！请听听这个语调极其稳健的版本：{output_wav}")

if __name__ == "__main__":
    run_v47_acoustic_anchor()

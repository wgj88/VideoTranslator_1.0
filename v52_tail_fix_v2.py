# -*- coding: utf-8 -*-
import os, sys, json, subprocess, numpy as np, soundfile as sf
import whisper

# 物理注入 FFmpeg 路径
FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

sys.path.append(r"E:\VideoTranslator_Project")
from clone_dubber import VideoCloneDubber

def run_v2_protector():
    print(f"\n[V52.1-v2] 启动【尾音保全】终极修复...")
    
    script_p = r"E:\VideoTranslator_Project\separated_audio\V51_CALIBRATED_SCRIPT.json"
    with open(script_p, "r", encoding="utf-8") as f: data = json.load(f)
    
    role_lib_p = r"E:\VideoTranslator_Project\temp_factory\v9_role_library.json"
    with open(role_lib_p, "r") as f: seed_p = json.load(f)['SPEAKER_00']['wav']
    
    db = VideoCloneDubber()
    auditor = whisper.load_model("base")

    processed_list = []
    # 只处理 2 分钟后的最后几段
    for i in range(15, len(data)):
        item = data[i]
        safe_text = item['zh'].strip() + "。"
        print(f"  -> [{i+1}/{len(data)}] 正在雕琢: {safe_text}")
        
        wav = db.model.generate(text=safe_text, reference_wav_path=seed_p, inference_timesteps=50)
        temp_raw = f"E:\\VideoTranslator_Project\\temp_factory\\v52_v2_raw_{i}.wav"
        sf.write(temp_raw, wav, db.sample_rate)
        
        # Whisper 精准审计结束点
        res = auditor.transcribe(temp_raw, verbose=False)
        last_word_end = res['segments'][-1]['end'] if res['segments'] else len(wav)/db.sample_rate
        
        # 保护性留白 0.25s
        final_end = last_word_end + 0.25
        output_p = f"E:\\VideoTranslator_Project\\temp_factory\\v52_v2_fixed_{i}.wav"
        
        # 执行柔和切除
        cmd = [
            FFMPEG_BIN, "-y", "-i", temp_raw,
            "-af", f"atrim=end={final_end},asetpts=PTS-STARTPTS,afade=t=out:st={last_word_end}:d=0.2",
            output_p
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        processed_list.append((output_p, item['start']))

    # 局部合成验证
    print("\n[V52.1-v2] 执行局部缝合...")
    test_wav = r"E:\VideoTranslator_Project\output_final\V52_END_VOICE_AUDIT_V2.wav"
    input_args = []
    filter_parts = []
    for idx, (p, start) in enumerate(processed_list):
        input_args.extend(["-i", p])
        delay = int((start - 120) * 1000)
        filter_parts.append(f"[{idx}:a]adelay={delay}|{delay}[a{idx}]")
    
    mix_str = "".join([f"[a{k}]" for k in range(len(processed_list))]) + f"amix=inputs={len(processed_list)}"
    subprocess.run([FFMPEG_BIN, "-y"] + input_args + ["-filter_complex", ";".join(filter_parts) + ";" + mix_str, test_wav], check=True)
    print(f"✅ V52.1-v2 完成！文件：{test_wav}")

if __name__ == "__main__":
    run_v2_protector()

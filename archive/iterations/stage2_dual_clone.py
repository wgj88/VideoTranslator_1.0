# -*- coding: utf-8 -*-
import os, sys, json, subprocess, whisper
import soundfile as sf
import numpy as np

# --- 环境补丁 ---
FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

sys.path.append(r"E:\VideoTranslator_Project")
from clone_dubber import VideoCloneDubber

def run_stage2():
    json_path = r"E:\VideoTranslator_Project\separated_audio\v4_balanced_script.json"
    vocal_src = r"C:\Users\Administrator\separated_audio\pure_vocals.wav"
    temp_dir = r"E:\VideoTranslator_Project\temp_factory"
    
    with open(json_path, "r", encoding="utf-8-sig") as f:
        data = json.load(f)

    # 1. 寻找最佳采样点
    speakers = ['SPEAKER_574', 'SPEAKER_127']
    seeds = {}
    
    print("\n[Stage 2] 正在提取角色黄金指纹...")
    ts_model = whisper.load_model("base")

    for spk in speakers:
        # 寻找该角色说话最长的一段
        spk_segs = [d for d in data if d['speaker'] == spk]
        if not spk_segs:
            print(f"  ⚠️ 警告: 未发现 {spk} 的有效片段")
            continue
        
        best_seg = max(spk_segs, key=lambda x: x['end'] - x['start'])
        seed_p = os.path.join(temp_dir, f"{spk}_seed.wav")
        
        # 截取
        start = best_seg['start']
        dur = min(5, best_seg['end'] - start)
        subprocess.run([FFMPEG_BIN, "-y", "-i", vocal_src, "-ss", str(start), "-t", str(dur), seed_p], check=True, capture_output=True)
        
        # 识别种子文本 (双向引导的关键)
        res = ts_model.transcribe(seed_p)
        seeds[spk] = {"wav": seed_p, "text": res['text'].strip()}
        print(f"  ✅ {spk} 采样成功: '{seeds[spk]['text'][:30]}...'")

    # 2. 模拟对话配音
    db = VideoCloneDubber()
    test_cases = [
        {"text": "大家好，我是 SPEAKER 574。我正在展示本届博览会的最新科技。", "spk": "SPEAKER_574"},
        {"text": "哇！我是 SPEAKER 127，这辆飞行汽车真的太不可思议了！", "spk": "SPEAKER_127"}
    ]
    
    audition_segments = []
    print("\n[Stage 2] 正在进行双角色克隆渲染...")
    
    for i, case in enumerate(test_cases):
        seed_info = seeds.get(case['spk'])
        if seed_info:
            wav = db.model.generate(
                text=case['text'], 
                prompt_wav_path=seed_info['wav'], 
                prompt_text=seed_info['text']
            )
            out_p = os.path.join(temp_dir, f"dual_test_{i}.wav")
            sf.write(out_p, wav, db.sample_rate)
            audition_segments.append(out_p)

    # 3. 合并试听包
    final_audit = r"E:\VideoTranslator_Project\output_final\DUAL_ROLE_AUDITION.wav"
    combined = np.concatenate([sf.read(p)[0] for p in audition_segments])
    sf.write(final_audit, combined, db.sample_rate)
    
    print(f"\n🏆 第二阶段大捷！请前往试听双角色对比效果：{final_audit}")

if __name__ == "__main__":
    run_stage2()

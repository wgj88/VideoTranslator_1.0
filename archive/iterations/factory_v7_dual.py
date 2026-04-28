# -*- coding: utf-8 -*-
import os, sys, json, subprocess, re, numpy as np
import soundfile as sf
import librosa, torch

# --- 环境补丁 ---
FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

def ffmpeg_robust_load(path, sr=None, **kwargs):
    target_sr = sr if sr else 44100
    cmd = [FFMPEG_BIN, "-y", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(target_sr), "pipe:1"]
    proc = subprocess.run(cmd, capture_output=True, check=True)
    return np.frombuffer(proc.stdout, dtype=np.float32), target_sr
librosa.load = ffmpeg_robust_load

sys.path.append(r"E:\VideoTranslator_Project")
from clone_dubber import VideoCloneDubber
from transcriber import AudioTranscriber

def run_v7_dual_speaker():
    v_mp4 = r"E:\VideoTranslator_Project\raw_videos\Vlog ｜ New technology paves way for better life at CICPE.mp4"
    j_zh = r"E:\VideoTranslator_Project\raw_videos\Vlog ｜ New technology paves way for better life at CICPE_zh.json"
    
    # 锁定双角色种子
    seed_female = r"E:\VideoTranslator_Project\output_final\OUTLIER_SCAN_SPK_0.wav"
    seed_male = r"E:\VideoTranslator_Project\output_final\OUTLIER_SCAN_SPK_2.wav"
    
    ts = AudioTranscriber()
    db = VideoCloneDubber()
    
    print("\n[V7.0] 正在识别双角色音色指纹...")
    ref_text_f = ts.model.transcribe(seed_female)['text'].strip()
    ref_text_m = ts.model.transcribe(seed_male)['text'].strip()
    
    with open(j_zh, "r", encoding="utf-8-sig") as f: data = json.load(f)

    temp_dir = r"E:\VideoTranslator_Project\temp_factory\v7_wavs"
    os.makedirs(temp_dir, exist_ok=True)
    
    final_segments = []
    print("\n[V7.0] 正在启动【双角色动态切换】配音渲染...")

    # 我们处理前 10 句
    for i in range(10):
        item = data[i]
        text = re.sub(r'\(.*?\)|\[.*?\]', '', item.get('translated_text', '')).strip()
        if not text: continue
        
        # --- 角色动态分配逻辑 ---
        # 25s 以后切换为男声，其余为女声
        if item['start'] > 24.0:
            current_seed = seed_male
            current_ref_text = ref_text_m
            role_name = "MALE_GUEST"
        else:
            current_seed = seed_female
            current_ref_text = ref_text_f
            role_name = "FEMALE_HOST"
        
        print(f"  -> [{role_name}] 渲染第 {i} 句: {text[:15]}...")
        wav = db.model.generate(text="……" + text + "。", prompt_wav_path=current_seed, prompt_text=current_ref_text)
        
        out_p = os.path.join(temp_dir, f"v7_dub_{i}.wav")
        sf.write(out_p, wav, db.sample_rate)
        
        # 物理消噪与淡出
        clean_p = out_p.replace(".wav", "_clean.wav")
        subprocess.run([FFMPEG_BIN, "-y", "-i", out_p, "-af", "silenceremove=stop_periods=1:stop_duration=0.05:stop_threshold=-45dB,atrim=start=0.2,afade=t=out:st=1.3:d=0.1", clean_p], capture_output=True)
        
        # 应用时间轴对齐
        delay = int(item['start'] * 1000)
        aligned_p = out_p.replace(".wav", "_aligned.wav")
        subprocess.run([FFMPEG_BIN, "-y", "-i", clean_p, "-af", f"adelay={delay}|{delay}", aligned_p], check=True, capture_output=True)
        final_segments.append(aligned_p)

    # 5. 终极物理混合
    output_video = r"E:\VideoTranslator_Project\output_final\V7_0_DUAL_SPEAKER_FINAL.mp4"
    bgm = r"C:\Users\Administrator\separated_audio\pure_bgm.wav"
    
    input_args = []
    for s in final_segments: input_args.extend(["-i", s])
    
    # 构造滤镜
    mix_zh = "".join([f"[{k+2}:a]" for k in range(len(final_segments))])
    filter_complex = f"{mix_zh}amix=inputs={len(final_segments)}:duration=longest,volume={len(final_segments)}[dub];"
    filter_complex += f"[1:a][dub]sidechaincompress=threshold=0.01:ratio=20[bg];"
    filter_complex += "[bg][dub]amix=inputs=2:weights='0.1 1.0'[out]"
    
    cmd = [FFMPEG_BIN, "-y", "-i", v_mp4, "-i", bgm] + input_args + ["-filter_complex", filter_complex, "-map", "0:v", "-map", "[out]", "-c:v", "copy", "-c:a", "aac", output_video]
    
    print("\n[V7.0] 正在执行最后的物理压制...")
    subprocess.run(cmd, check=True)
    print(f"\n🏆 V7.0 多角色终极作品已产出：{output_video}")

if __name__ == "__main__":
    run_v7_dual_speaker()

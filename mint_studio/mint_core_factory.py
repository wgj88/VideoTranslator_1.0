
import os
import sys
import json
import re
import subprocess
import time
import torch
import soundfile as sf
import librosa
import numpy as np
import gc
from pathlib import Path
from tqdm import tqdm
from voxcpm import VoxCPM
from mint_config import MintConfig as cfg

def build_atempo_chain(tempo):
    """递归构建变速链，打破 FFmpeg 2.0x 物理极限"""
    filters = []
    t = tempo
    while t > 2.0:
        filters.append("atempo=2.0")
        t /= 2.0
    while t < 0.5:
        filters.append("atempo=0.5")
        t /= 0.5
    filters.append(f"atempo={t:.4f}")
    return ",".join(filters)

def compute_entropy(y, bins=100):
    """计算波形熵值 (归一化到 0-1)，衡量信号复杂度"""
    if np.max(np.abs(y)) < 1e-6: return 0.0
    hist, _ = np.histogram(y, bins=bins, range=(-1, 1))
    probs = hist / len(y)
    probs = probs[probs > 0]
    return -np.sum(probs * np.log2(probs)) / np.log2(bins)

def quality_check(wav, seg_idx):
    """三指标联合质检：捕捉削波、能量失控和低熵失真"""
    peak = np.max(np.abs(wav))
    rms_db = 20 * np.log10(np.sqrt(np.mean(wav**2)) + 1e-9)
    entropy = compute_entropy(wav)
    
    issues = []
    if peak > 0.95:        issues.append(f"Peak={peak:.3f} 削波风险")
    if rms_db > -16:       issues.append(f"RMS={rms_db:.1f}dB 能量失控")
    if entropy < 0.60:     issues.append(f"Entropy={entropy:.2f} 低熵失真")
    
    if issues:
        print(f"\n[!] 段落 {seg_idx} 质检失败: {' | '.join(issues)}")
        return False
    return True

def load_clean_engine():
    """重新初始化 AI 引擎，彻底清理显存与内存"""
    print(f"\n[*] 正在执行引擎冷重置 (Cold Boot + GC)...")
    gc.collect()
    torch.cuda.empty_cache()
    # 彻底释放旧实例
    if 'model' in globals():
        del globals()['model']
    
    model = VoxCPM.from_pretrained(str(cfg.MODEL_WEIGHTS), load_denoiser=False)
    model.tts_model.temperature = 0.1 
    return model

def generate_safe(model, text, reference_wav_path):
    """带 KV Cache 清理的安全推理"""
    if hasattr(model, 'reset_cache'):
        model.reset_cache()
    torch.cuda.empty_cache()
    return model.generate(text=text, reference_wav_path=str(reference_wav_path), cfg_value=2.0)

def run_apex_production_v22_restored(vtt_path, video_name, limit_seconds=480):
    print(f"\n{'='*20} Project Mint V22.0: 屠龙标准版 (RESTORED) {'='*20}")
    cfg.ensure_dirs()
    
    # 1. 脚本解析
    with open(vtt_path, "r", encoding="utf-8") as f: content = f.read()
    blocks = re.findall(r"(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})\n(.*?)(?:\n\n|$)", content, re.DOTALL)
    def to_sec(t):
        p = re.split('[:.]', t)
        return int(p[0])*3600 + int(p[1])*60 + int(p[2]) + int(p[3])/1000.0
    segs = [{"start": to_sec(s), "end": to_sec(e), "zh": txt.replace("\n", " ").strip()} for s, e, txt in blocks if to_sec(s) < limit_seconds]

    # 2. 初始化
    model = load_clean_engine()
    results = []
    chunk_dir = cfg.OUTPUT_DIR / "chunks"
    
    # 3. 生产循环
    print(f"🎙️ 启动 V22.0 标准流水线...")
    for i, item in enumerate(tqdm(segs)):
        # 策略 1: 每 10 段重置引擎
        if i > 0 and i % cfg.REINIT_EVERY == 0:
            model = load_clean_engine()

        # 策略 2: 种子轮换
        current_seed = cfg.SEED_POOL[i // cfg.REINIT_EVERY % len(cfg.SEED_POOL)]
        clean_text = f"[ZH]{item['zh'].strip('。？！， ')}。"
        quota = (segs[i+1]["start"] if i < len(segs)-1 else item["end"]) - item["start"]
        
        # 策略 3: 质检重试 (最多3次)
        wav = None
        for attempt in range(3):
            wav = generate_safe(model, clean_text, current_seed)
            if quality_check(wav, i):
                break
            print(f"     [!] 触发重试 ({attempt+1}/2)...")
        
        raw_p = chunk_dir / f"raw_{i:03d}.wav"
        sf.write(raw_p, wav, model.tts_model.sample_rate)
        
        # 物理分析
        y, sr = librosa.load(raw_p, sr=model.tts_model.sample_rate)
        intervals = librosa.effects.split(y, top_db=cfg.VAD_TOP_DB)
        phys_end = intervals[-1][1] / sr if len(intervals) > 0 else len(y) / sr
        safe_boundary = max(quota - 0.05, 0.1)
        tempo = min(cfg.MAX_TEMPO, max(1.0, phys_end / safe_boundary))
        
        # 策略 4: 完美滤镜链顺序 (降噪 -> 变速 -> 归一化 -> 裁剪 -> 限幅 -> 淡出)
        final_p = chunk_dir / f"final_{i:03d}.wav"
        atempo_chain = build_atempo_chain(tempo)
        af_chain = (
            f"afftdn=nf=-40,"                   # 1. 降噪
            f"asetpts=PTS-STARTPTS,"
            f"{atempo_chain},"                   # 2. 变速
            f"dynaudnorm=p=0.95:m=10:s=5,"       # 3. 动态能量平抑
            f"atrim=end={safe_boundary},"         # 4. 物理裁剪
            f"asoftclip=type=tanh,"              # 5. 软削波双保险
            f"alimiter=limit=0.90:attack=1:release=20:level=disabled," # 6. 1ms 极速限幅
            f"afade=t=out:st={max(safe_boundary-0.05, 0.1)}:d=0.05"    # 7. 最终淡出
        )
        
        subprocess.run(['ffmpeg', '-y', '-i', str(raw_p), '-af', af_chain, '-ar', '48000', str(final_p)], capture_output=True)
        results.append((str(final_p), item["start"]))

    # 4. 母带混音 (48kHz + 1ms Limiter)
    print("[*] 正在执行全平衡母带混音...")
    output_master_wav = cfg.OUTPUT_DIR / "master_zh_purified.wav"
    in_args = []
    delays = []
    for idx, (p, start_t) in enumerate(results):
        in_args.extend(["-i", p])
        delays.append(f"[{idx}:a]adelay={int(start_t*1000)}|{int(start_t*1000)},volume=0.8[a{idx}]")
    
    mix_cmd = "".join(f"[a{k}]" for k in range(len(results))) + \
              f"amix=inputs={len(results)}:duration=longest:normalize=0," + \
              f"alimiter=limit=0.8:attack=1:release=50," + \
              f"loudnorm=I={cfg.LOUDNESS_TARGET}:TP=-1.5:LRA=7[aout]"
    
    subprocess.run(['ffmpeg', '-y'] + in_args + ['-filter_complex', ";".join(delays) + ";" + mix_cmd, '-map', '[aout]', '-ar', '48000', str(output_master_wav)], check=True)

    # 5. 最终封装
    print("[*] 正在执行最终声画合体...")
    final_video = cfg.OUTPUT_DIR / f"MINT_V22_FINAL_RESTORED_{int(time.time())}.mp4"
    bgm_p = cfg.get_bgm_path(video_name)
    cmd = ['ffmpeg', '-y', '-i', str(cfg.RAW_VIDEO_DIR / video_name), '-i', str(output_master_wav)]
    
    # 侧链闪避逻辑 (V16.4/V16.6 风格，非暴力模式)
    filter_complex = "[1:a]volume=1.0,compand=attacks=0.1:decays=0.1:points=-70/-70|-25/-20|0/-2,asplit=2[zh_for_sc][zh_for_mix]"
    if bgm_p:
        cmd.extend(['-i', str(bgm_p)])
        filter_complex += f";[2:a]volume=0.8,aresample=48000[bg_clean];[bg_clean][zh_for_sc]sidechaincompress=threshold=0.1:ratio=4:attack=20:release=400[bg_ducked];[zh_for_mix][bg_ducked]amix=inputs=2:duration=first:normalize=0[aout]"
    else:
        filter_complex += f";[0:a]pan=mono|c0=c0-c1,aresample=48000[orig_killed];[orig_killed][zh_for_sc]sidechaincompress=threshold=0.1:ratio=8:attack=15:release=500[bg_ducked];[zh_for_mix][bg_ducked]amix=inputs=2:duration=first:normalize=0[aout]"
    
    cmd.extend(['-filter_complex', filter_complex, '-map', '0:v', '-map', '[aout]', '-c:v', 'copy', '-c:a', 'aac', '-ar', '48000', '-b:a', '256k', str(final_video)])
    subprocess.run(cmd, check=True)
    print(f"\n🎉 V22.0 巅峰还原版完成: {final_video}")

if __name__ == "__main__":
    vtt = cfg.PROJECT_ROOT / "raw_videos/Is This the Best Modern House in the World？ (House Tour).zh-Hans.vtt"
    run_apex_production_v22_restored(vtt, "house_tour_ready.mp4")

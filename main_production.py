# -*- coding: utf-8 -*-
"""
VideoTranslator 1.0 - Official Production Entry
Architecture: V106 (Anchor Stability + Collision Guard + NLP Intervention)
"""
import os, sys, json, subprocess, time
import soundfile as sf
import librosa

# 导入中央配置
sys.path.insert(0, os.path.join(r"E:\VideoTranslator_Project", "core_engines"))
import config
from clone_dubber import VideoCloneDubber

def simple_nlp_shorten(text):
    rules = {"将会有": "将有", "将会": "将", "成为了": "成了", "成为": "成", "我曾经": "我曾", "已经": "已"}
    short = text
    for k, v in rules.items(): short = short.replace(k, v)
    return short

def run_production(script_name="UNHINGED_FINAL_506_SCRIPT.json", video_name="The unhinged world of tech in 2026....f399.mp4", limit_seconds=60):
    print("\n" + "🎬"*10 + " VideoTranslator 正式生产线 " + "🎬"*10)
    
    # 路径准备
    script_p = os.path.join(config.ROOT_DIR, "unhinged_tech", script_name)
    raw_v    = os.path.join(config.ROOT_DIR, "raw_videos", video_name)
    bgm_p    = os.path.join(config.ROOT_DIR, "unhinged_tech", "separated", "other.wav")
    srt_p    = os.path.join(config.ROOT_DIR, "unhinged_tech", "v81_final.srt")
    
    inter_dir = os.path.join(config.WORKSPACE, "chunks")
    os.makedirs(inter_dir, exist_ok=True)
    
    output_wav = os.path.join(config.WORKSPACE, "master_zh.wav")
    output_mp4 = os.path.join(config.OUTPUT_DIR, f"PRODUCTION_{int(time.time())}.mp4")

    with open(script_p, "r", encoding="utf-8") as f:
        data = json.load(f)
    segs = [it for it in data if it["start"] < limit_seconds]

    db = VideoCloneDubber(model_path=config.MODEL_WEIGHTS)
    t0 = time.time()
    results = []

    print(f"[*] 开始处理 {len(segs)} 段配音...")
    for i, item in enumerate(segs):
        zh = item["zh"].strip().strip("。？！， ")
        quota = (segs[i+1]["start"] if i < len(segs)-1 else item["end"]) - item["start"]
        
        # NLP 预处理
        current_text = simple_nlp_shorten(zh) if len(zh)/quota > config.MIN_CPS else zh

        # 生成 (全局锚点模式)
        raw_p = os.path.join(inter_dir, f"raw_{i}.wav")
        wav = db.generate_safe(text=current_text, reference_wav_path=config.DEFAULT_SEED)
        sf.write(raw_p, wav, db.sample_rate)

        # 物理分析
        y, sr = sf.read(raw_p)
        intervals = librosa.effects.split(y, top_db=config.VAD_TOP_DB)
        phys_end = intervals[-1][1] / sr if len(intervals) > 0 else len(y) / sr
        
        safe_boundary = quota - 0.05
        tempo = max(1.0, phys_end / safe_boundary)
        
        if tempo > config.MAX_TEMPO:
            print(f"  [Alert] Seg {i} 语速过快 ({tempo:.2f}x)")

        final_p = os.path.join(inter_dir, f"final_{i}.wav")
        subprocess.run([
            config.FFMPEG_BIN, "-y", "-i", raw_p, "-af",
            f"atrim=end={phys_end},asetpts=PTS-STARTPTS,atempo={tempo},atrim=end={safe_boundary},afade=t=out:st={max(safe_boundary-0.05, 0.1)}:d=0.05",
            final_p
        ], capture_output=True)

        results.append((final_p, item["start"]))
        print(f"  [{i+1}/{len(segs)}] {current_text[:12]}... OK")

    # 混音
    in_args = []
    delays = []
    for idx, (p, start_t) in enumerate(results):
        in_args.extend(["-i", p])
        delays.append(f"[{idx}:a]adelay={int(start_t*1000)}|{int(start_t*1000)}[a{idx}]")
    mix_cmd = "".join(f"[a{k}]" for k in range(len(results))) + f"amix=inputs={len(results)}:duration=longest[aout]"
    subprocess.run([config.FFMPEG_BIN, "-y"] + in_args + ["-filter_complex", ";".join(delays) + ";" + mix_cmd, "-map", "[aout]", "-c:a", "pcm_s16le", output_wav], check=True, capture_output=True)

    # 合成
    srt_escaped = srt_p.replace("\\", "/").replace(":", "\\:")
    cmd_pack = [
        config.FFMPEG_BIN, "-y", "-ss", "0", "-t", str(limit_seconds), "-i", raw_v, "-i", output_wav, "-ss", "0", "-t", str(limit_seconds), "-i", bgm_p,
        "-filter_complex", f"[1:a]volume=1.5[zh];[2:a]volume=0.2[bg];[zh][bg]amix=inputs=2:duration=first[a_final];[0:v]subtitles='{srt_escaped}':force_style='FontSize=18,Alignment=2'[v_final]",
        "-map", "[v_final]", "-map", "[a_final]", "-c:v", "libx264", "-crf", "23", "-preset", "veryfast", output_mp4
    ]
    subprocess.run(cmd_pack, check=True, capture_output=True)
    print(f"\n✨ 生产完成！\n总耗时: {time.time()-t0:.1f}s\n产出文件: {output_mp4}")

if __name__ == "__main__":
    run_production()

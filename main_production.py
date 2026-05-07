# -*- coding: utf-8 -*-
"""
VideoTranslator 1.0 - Refactored Official Entry
Fixed: master loudness normalization (V16.4), atempo chain, and boundary safety.
"""
import os, sys, json, subprocess, time
import soundfile as sf
import librosa

# 导入中央配置
sys.path.insert(0, os.path.join(r"E:\VideoTranslator_Project", "core_engines"))        
import config
from clone_dubber import VideoCloneDubber

def build_atempo_chain(tempo):
    """将超限 tempo 拆成多个 atempo 滤镜链，解决 FFmpeg 2.0 限制"""
    filters = []
    while tempo > 2.0:
        filters.append("atempo=2.0")
        tempo /= 2.0
    while tempo < 0.5:
        filters.append("atempo=0.5")
        tempo /= 0.5
    filters.append(f"atempo={tempo:.4f}")
    return ",".join(filters)

def simple_nlp_shorten(text):
    rules = {"将会有": "将有", "将会": "将", "成为了": "成了", "成为": "成", "我曾经": "我曾", "已经": "已"}
    short = text
    for k, v in rules.items(): short = short.replace(k, v)
    return short

def run_production(script_name, video_name, bgm_name=None, srt_name=None, limit_seconds=60):
    print("\n" + "🎬"*10 + " VideoTranslator 生产启动 (V16.4 Final) " + "🎬"*10)

    script_p = os.path.join(config.ROOT_DIR, "unhinged_tech", script_name)
    raw_v    = os.path.join(config.ROOT_DIR, "raw_videos", video_name)
    bgm_p = os.path.join(config.ROOT_DIR, "unhinged_tech", "separated", bgm_name) if bgm_name else None
    srt_p = os.path.join(config.ROOT_DIR, "unhinged_tech", srt_name) if srt_name else None

    inter_dir = os.path.join(config.WORKSPACE, "chunks")
    os.makedirs(inter_dir, exist_ok=True)

    output_wav = os.path.join(config.WORKSPACE, "master_zh.wav")
    output_mp4 = os.path.join(config.OUTPUT_DIR, f"PRODUCTION_{int(time.time())}.mp4") 

    with open(script_p, "r", encoding="utf-8") as f:
        data = json.load(f)
    segs = [it for it in data if it["start"] < limit_seconds]

    db = VideoCloneDubber(model_path=config.MODEL_WEIGHTS)
    results = []

    print(f"[*] 处理中: {video_name} | 段落: {len(segs)}")
    for i, item in enumerate(segs):
        zh = item["zh"].strip().strip("。？！， ") + "。"
        quota = (segs[i+1]["start"] if i < len(segs)-1 else item["end"]) - item["start"]

        current_text = simple_nlp_shorten(zh) if len(zh)/quota > config.MIN_CPS else zh
        raw_p = os.path.join(inter_dir, f"raw_{i}.wav")
        wav = db.generate_safe(text=current_text, reference_wav_path=config.DEFAULT_SEED)
        sf.write(raw_p, wav, db.sample_rate)

        y, sr = sf.read(raw_p)
        intervals = librosa.effects.split(y, top_db=config.VAD_TOP_DB)
        phys_end = intervals[-1][1] / sr if len(intervals) > 0 else len(y) / sr        

        safe_boundary = max(quota - 0.05, 0.1)
        tempo = min(config.MAX_TEMPO, max(1.0, phys_end / safe_boundary))
        final_p = os.path.join(inter_dir, f"final_{i}.wav")

        af_chain = (
            f"atrim=end={phys_end + 0.1},asetpts=PTS-STARTPTS,"
            f"{build_atempo_chain(tempo)},"
            f"atrim=end={safe_boundary + 0.05},"
            f"afade=t=out:st={max(safe_boundary - 0.05, safe_boundary * 0.95)}:d=0.05"
        )

        subprocess.run([
            config.FFMPEG_BIN, "-y", "-i", raw_p, "-af", af_chain, final_p
        ], capture_output=True)
        results.append((final_p, item["start"]))

    # 混音 - V16.4 核心：应用 Master Loudnorm 消除音量跳变
    in_args = []
    delays = []
    for idx, (p, start_t) in enumerate(results):
        in_args.extend(["-i", p])
        delays.append(f"[{idx}:a]adelay={int(start_t*1000)}|{int(start_t*1000)}[a{idx}]")
    
    # 将 63 轨混合后立即进行响度归一化 (I=-12)，这会彻底抹平最后一句话的音量突变
    mix_cmd = "".join(f"[a{k}]" for k in range(len(results))) + f"amix=inputs={len(results)}:duration=longest:normalize=0,loudnorm=I=-12:TP=-1.5:LRA=7[aout]"
    subprocess.run([config.FFMPEG_BIN, "-y"] + in_args + ["-filter_complex", ";".join(delays) + ";" + mix_cmd, "-map", "[aout]", "-c:a", "pcm_s16le", output_wav], check=True, capture_output=True)

    # 合成 MP4
    cmd_pack = [config.FFMPEG_BIN, "-y", "-ss", "0", "-t", str(limit_seconds), "-i", raw_v, "-i", output_wav]
    # 在 1.8 倍放大的基础上，增加一个柔和的压限保护（compand），防止动态过载
    filter_complex = "[1:a]volume=1.8,compand=0.3|0.3:6:-70/-60|-20/-20|0/-3:6:0:-90:0.2[zh]"

    if bgm_p and os.path.exists(bgm_p):
        cmd_pack.extend(["-ss", "0", "-t", str(limit_seconds), "-i", bgm_p])
        filter_complex += ";[2:a]volume=0.2[bg];[zh][bg]amix=inputs=2:duration=first:normalize=0[a_out]"
    else:
        filter_complex += ";[zh]anull[a_out]"

    if srt_p and os.path.exists(srt_p):
        srt_esc = srt_p.replace("\\", "/").replace(":", "\\:")
        filter_complex += f";[0:v]subtitles='{srt_esc}':force_style='FontSize=18,Alignment=2'[v_out]"
    else:
        filter_complex += ";[0:v]copy[v_out]"

    cmd_pack.extend(["-filter_complex", filter_complex, "-map", "[v_out]", "-map", "[a_out]", "-c:v", "libx264", "-crf", "23", "-preset", "veryfast", output_mp4])
    subprocess.run(cmd_pack, check=True, capture_output=True)
    print(f"\n✨ 任务圆满完成！产出: {output_mp4}")

if __name__ == "__main__":
    # 默认跑全量 8 分钟测试 (约 480 秒)
    run_production("V107_HOUSE_SCRIPT.json", "house_tour_ready.mp4", None, None, 480)

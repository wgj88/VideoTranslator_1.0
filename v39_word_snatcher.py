# -*- coding: utf-8 -*-
import os, sys, json, subprocess, whisper, soundfile as sf
import numpy as np

FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

def run_v39_precision():
    print(f"\n[V39.1-Precision] 正在对 Seg 13 执行【词位锁死】手术...")
    
    # 物理定位 V34 产生的高清原始样片 (50-Step渲染的那个)
    raw_p = r"E:\VideoTranslator_Project\temp_factory\v34_final_wavs\raw_12.wav" # 注意：Line 13 对应的物理索引通常是 12
    if not os.path.exists(raw_p):
        print("❌ 找不到原始生成片段")
        return

    # 1. AI 词位分析
    print("  -> AI 正在扫描每个汉字的物理位置...")
    model = whisper.load_model("base")
    res = model.transcribe(raw_p, word_timestamps=True)
    
    all_words = []
    for seg in res['segments']:
        if 'words' in seg: all_words.extend(seg['words'])
    
    # 目标：这句台词大约 20 个中文字符
    # 我们取识别出的前 20 个字（或词）的终点
    target_count = 18 # 排除掉前面的冗余
    
    if len(all_words) > 0:
        # 我们寻找最后一个看起来像正常中文的词
        # 避开末尾那 3 秒钟的胡言乱语
        # 逻辑：取 2.6s 之前最后一个识别出的词（因为剧本时长是 2.56s）
        best_end = 0.0
        for w in all_words:
            if w['end'] < 3.0: # 只看 3 秒内的正常台词区间
                best_end = w['end']
        
        target_end_time = best_end
        print(f"  📍 语义终点确认: {target_end_time:.2f}s (已成功排除 3.0s 之后的幻觉内容)")
    else:
        target_end_time = 2.56

    # 2. 物理熔断
    output_p = r"E:\VideoTranslator_Project\output_final\V39_WORD_SNATCHER_RESULT.wav"
    cut_point = target_end_time + 0.05 # 留 50ms 尾音
    
    cmd_cut = [
        FFMPEG_BIN, "-y", "-i", raw_p,
        "-af", f"atrim=start=0.15:end={cut_point+0.15},asetpts=PTS-STARTPTS,afade=t=out:st={max(0, target_end_time-0.05)}:d=0.1",
        output_p
    ]
    subprocess.run(cmd_cut, check=True, capture_output=True)
    
    print(f"✅ V39 手术完成！")
    print(f"🏆 请听听结尾是否已经干净得“令人发指”：{output_p}")

if __name__ == "__main__":
    run_v39_precision()

# -*- coding: utf-8 -*-
import os, sys, subprocess
import whisper
import soundfile as sf

FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

def perform_word_surgery():
    print("\n" + "🗡️"*10 + " 启动 V77 纳米级单词对齐手术 " + "🗡️"*10)
    raw_03 = r"E:\VideoTranslator_Project\output_final\V75_RAW_SEG_03.wav"
    output_03 = r"E:\VideoTranslator_Project\output_final\V77_WORD_CLEAN_SEG_03.wav"
    
    # 1. 载入模型并开启单词级时间轴
    model = whisper.load_model("base")
    print("  -> 正在执行单词级声纹拆解...")
    
    # 强制指定初始剧本，让 Whisper 重点寻找这些字
    result = model.transcribe(raw_03, word_timestamps=True)
    
    # 2. 搜索最后一个目标字“了”
    # 我们从后往前找
    target_end = 0
    found = False
    for segment in reversed(result['segments']):
        for word in reversed(segment['words']):
            clean_word = word['word'].strip("，。！？")
            if "了" in clean_word:
                target_end = word['end']
                found = True
                print(f"  🎯 成功锁定目标字【了】：结束于 {target_end:.2f}s")
                break
        if found: break

    if not found:
        print("  ⚠️ 未能精准定位【了】，降级使用语义段终点。")
        target_end = result['segments'][-1]['end']

    # 3. 毫秒级硬切割
    # 相比 V76，我们这次不留缓冲，直接在字音结束处熔断
    cmd = [
        FFMPEG_BIN, "-y", "-i", raw_03,
        "-af", f"atrim=end={target_end},asetpts=PTS-STARTPTS,afade=t=out:st={max(0, target_end-0.05)}:d=0.05",
        output_03
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"\n✅ 03 段纳米级清洗完成！")
    print(f"📂 成品路径：{output_03}")

if __name__ == "__main__":
    perform_word_surgery()

# -*- coding: utf-8 -*-
import os, sys, json, subprocess
import whisper
import soundfile as sf

# 物理注入 FFmpeg 路径
FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

def perform_v2_surgery():
    print("\n" + "🩺"*10 + " 启动 V76-V2 精准切除手术 " + "🩺"*10)
    
    # 指向我们刚提取的嫌疑片段
    raw_03 = r"E:\VideoTranslator_Project\output_final\V75_RAW_SEG_03.wav"
    output_03 = r"E:\VideoTranslator_Project\output_final\V76_CLEAN_SEG_03.wav"
    
    if not os.path.exists(raw_03):
        print(f"❌ 找不到原始文件: {raw_03}")
        return

    # 1. 深度听写，锚定最后一个字的坐标
    model = whisper.load_model("base")
    print("  -> 正在对 03 段执行毫秒级语义扫描...")
    result = model.transcribe(raw_03, verbose=False)
    
    # 提取时间轴
    if not result['segments']:
        print("❌ 审计失败：未识别出任何文字。")
        return
        
    last_segment = result['segments'][-1]
    semantic_end = last_segment['end']
    text_content = result['text']
    
    # 2. 测量物理全长
    data, sr = sf.read(raw_03)
    physical_len = len(data) / sr
    
    print(f"  📊 手术数据汇报：")
    print(f"     - 剧本原文: {text_content}")
    print(f"     - 语义结束时刻: {semantic_end:.2f}s")
    print(f"     - 物理总长: {physical_len:.2f}s")
    print(f"     - 确认为幻觉杂音的长度: {physical_len - semantic_end:.2f}s")

    # 3. 执行“死亡切除”
    # 我们只给 0.05s 的边缘，然后直接淡出
    protected_cut = semantic_end + 0.05
    cmd = [
        FFMPEG_BIN, "-y", "-i", raw_03,
        "-af", f"atrim=end={protected_cut},asetpts=PTS-STARTPTS,afade=t=out:st={semantic_end}:d=0.1",
        output_03
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"\n✅ 03 段手术成功！幻觉“啊”已被物理蒸发。")
    print(f"📂 救治后的文件：{output_03}")

if __name__ == "__main__":
    perform_v2_surgery()

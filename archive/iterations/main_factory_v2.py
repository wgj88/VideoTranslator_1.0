# -*- coding: utf-8 -*-
import os, sys, time

try:
    from static_ffmpeg import add_paths
    add_paths()
    ffmpeg_bin = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32"
    os.environ["PATH"] = ffmpeg_bin + os.pathsep + os.environ["PATH"]
except: pass

sys.path.append(r"E:\VideoTranslator_Project")
from trend_sniffer import TrendSniffer
from video_filter import VideoFilter
from editor_agent import EditorAgent
from downloader import VideoDownloader
from transcriber import AudioTranscriber
from translator import VideoTranslator
from clone_dubber import VideoCloneDubber
from cloner_tools import extract_reference_audio
from composer import VideoComposer

def start_v2_factory():
    print("\n" + "🚀"*10 + " 自动化工厂 V2.0：原音复刻版启动 " + "🚀"*10)
    
    # 初始化
    ts = AudioTranscriber(model_size="base")
    vt = VideoTranslator()
    db = VideoCloneDubber()
    cp = VideoComposer()
    sniffer = TrendSniffer()

    # 1. 寻找今日猎物
    candidates = sniffer.sniff()
    # 为演示，直接用刚才下载好的科技 Vlog
    target_video = r"E:\VideoTranslator_Project\raw_videos\Vlog ｜ New technology paves way for better life at CICPE.mp4"
    print(f"🎬 锁定目标: {target_video}")

    # 2. 核心黑科技：音色指纹提取
    print("\n[V2.0] 正在提取原音色指纹...")
    ref_wav = extract_reference_audio(target_video, start_time=5, duration=6)
    ref_text = ts.model.transcribe(ref_wav)['text'].strip()
    print(f"🎤 成功复刻音色。参考文本: {ref_text[:30]}...")

    # 3. 听译与深度翻译
    print("\n[V2.0] 正在进行听译与 LLM 汉化...")
    raw_json = ts.process(target_video)
    zh_json = vt.translate_json(raw_json)

    # 4. 全篇克隆配音 (默认开启)
    print("\n[V2.0] 正在生成【同音色】中文配音...")
    db.process_json_cloning(zh_json, ref_wav, ref_text, limit=15) # 演示限制 15 句

    # 5. 合成
    print("\n[V2.0] 正在合成终极成品...")
    final_video = cp.compose(target_video, zh_json, target_video)
    
    if final_video:
        print(f"\n🎊 恭喜！原音色汉化大片已产出：{final_video}")

if __name__ == "__main__":
    start_v2_factory()

# -*- coding: utf-8 -*-
import os, sys
from downloader import VideoDownloader
from transcriber import AudioTranscriber
from translator import VideoTranslator
from dubber import VideoDubber
from composer import VideoComposer

def run_full_pipeline(url):
    print("\n=== 🎬 [VideoOverseas] 自动化汉化工厂开工 ===")
    
    # 1. 搜集资源
    dl = VideoDownloader()
    if not dl.download(url): return
    
    # 获取文件名
    raw_files = [f for f in os.listdir("raw_videos") if f.endswith(".mp4")]
    if not raw_files: return
    latest_video = os.path.join("raw_videos", sorted(raw_files)[-1])
    
    # 2. 听译原文
    ts = AudioTranscriber(model_size="base")
    json_path = ts.process(latest_video)
    
    # 3. 深度汉化
    vt = VideoTranslator()
    zh_json = vt.translate_json(json_path)
    
    # 4. AI 配音
    db = VideoDubber()
    ready_json = db.process_json(zh_json)
    
    # 5. GPU 极速合成
    cp = VideoComposer()
    cp.compose(latest_video, ready_json)
    
    print("\n🎊 全链路任务成功！请检阅 output_final 中的大片。")

if __name__ == "__main__":
    # 使用确认为在线的“Special Day”短片
    test_url = "https://www.youtube.com/watch?v=R0yD2eS0R-Y" 
    run_full_pipeline(test_url)

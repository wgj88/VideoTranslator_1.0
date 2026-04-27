# -*- coding: utf-8 -*-
import os, sys, time

try:
    from static_ffmpeg import add_paths
    add_paths()
except:
    pass

from trend_sniffer import TrendSniffer
from browser_sniffer_class import BrowserSniffer
from video_filter import VideoFilter
from editor_agent import EditorAgent
from downloader import VideoDownloader
from transcriber import AudioTranscriber
from translator import VideoTranslator
from dubber import VideoDubber
from composer import VideoComposer
from quality_guard import QualityGuard # 引入守卫

def run_production_line():
    sniffer = TrendSniffer()
    checker = VideoFilter()
    editor = EditorAgent()
    dl = VideoDownloader()
    ts = AudioTranscriber(model_size="base")
    guard = QualityGuard() # 实例化守卫
    vt = VideoTranslator()
    db = VideoDubber()
    cp = VideoComposer()

    print("\n[1/7] 全网嗅探中...")
    candidates = sniffer.sniff()
    
    for url in candidates:
        print(f"\n[2/7] 正在审稿: {url}")
        passed, meta = checker.check(url)
        if not (passed and editor.review(meta)['passed']): 
            print("  ❌ 审稿未通过。")
            continue
        
        print(f"\n[3/7] 正在下载素材: {meta.get('title')}")
        if not dl.download(url): continue

        # 定位下载好的 MP4
        video_path = None
        for f in os.listdir("raw_videos"):
            if meta.get('title')[:20] in f and f.endswith(".mp4"):
                video_path = os.path.join("raw_videos", f)
                break
        
        if not video_path: continue

        print(f"\n[4/7] 正在听译原文: {video_path}")
        raw_json = ts.process(video_path)
        
        # --- 🚨 关键质检关卡 ---
        print("\n[5/7] 正在进行【素材质量审计】...")
        q_passed, q_reason = guard.check_transcript(raw_json)
        if not q_passed:
            print(f"  ❌ 审计未通过: {q_reason} (跳过该视频以节省资源)")
            continue
        print(f"  ✅ 审计通过: 文本质量达标。")

        print("\n[6/7] 正在翻译与配音...")
        zh_json = vt.translate_json(raw_json)
        # 演示模式只配 10 句
        db.process_json(zh_json, limit=10)

        print("\n[7/7] 最终合成中...")
        cp.compose(video_path, zh_json, video_path)

if __name__ == "__main__":
    run_production_line()

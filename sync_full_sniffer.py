# -*- coding: utf-8 -*-
import os, sys, json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from trend_sniffer import TrendSniffer
from browser_sniffer_class import BrowserSniffer
from video_filter import VideoFilter
from editor_agent import EditorAgent
from downloader import VideoDownloader

def run_smart_mission():
    print("\n" + "="*60)
    print("🤖 [VideoOverseas] 智能主编：全自动趋势猎取模式启动")
    print("="*60 + "\n")

    ts = TrendSniffer()
    bs = BrowserSniffer()
    vf = VideoFilter()
    editor = EditorAgent()
    dl = VideoDownloader()

    # 1. 搜集候选池
    print("[1/4] 正在多维度探测全球趋势...")
    candidates = {}
    for u in ts.sniff(): candidates[u] = "Search"
    for v in bs.sniff(): candidates[v['url']] = "Browser"
    
    print(f"\n[2/4] 原始候选池建立完成，共 {len(candidates)} 个视频。")

    # 2. 物理与智能双重过滤
    approved_list = []
    for url, src in candidates.items():
        # A. 物理过滤 (时长/分辨率等)
        phys_passed, meta = vf.check(url)
        if not phys_passed: continue
        
        # B. 智能主编审稿
        result = editor.review(meta)
        if result['passed']:
            print(f"  ✅ [审稿通过] 分数:{result['score']} | {meta.get('title')}")
            print(f"     理由: {result['reason']}")
            approved_list.append(url)
        else:
            print(f"  ❌ [审稿拒绝] {meta.get('title')[:40]}...")

    # 3. 结果执行
    print(f"\n[3/4] 审稿结束。今日黄金清单：{len(approved_list)} 个目标。")
    
    success_count = 0
    for url in approved_list:
        if dl.download(url):
            success_count += 1
            if success_count >= 2: break # 每日精选 2 个，保证精品率

    print(f"\n[4/4] 🏁 任务达成。已成功捕获 {success_count} 个具有爆款潜力的素材。")

if __name__ == "__main__":
    run_smart_mission()

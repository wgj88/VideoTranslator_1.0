# -*- coding: utf-8 -*-
from playwright.sync_api import sync_playwright
import time

def brush_trending_videos():
    print("[Browser] 启动浏览器环境...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True) # 使用无头模式提高效率
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            proxy={"server": "http://127.0.0.1:7890"}
        )
        page = context.new_page()
        
        print("[Browser] 正在打开 YouTube Trending 榜单...")
        try:
            page.goto("https://www.youtube.com/feed/trending", wait_until="domcontentloaded", timeout=60000)
            
            # 1. 模拟“刷”的动作：向下滚动三次
            for i in range(3):
                print(f"[Browser] 正在向下刷视频 (第 {i+1} 次滚动)...")
                page.mouse.wheel(0, 2000)
                time.sleep(2) # 等待新内容加载
            
            # 2. 使用更宽泛的选择器抓取视频列表
            # YouTube 的视频标题通常在 h3 下的 a 标签中
            video_elements = page.query_selector_all("ytd-video-renderer")
            
            print(f"[Browser] 页面渲染完成，检测到 {len(video_elements)} 个视频条目。")
            
            results = []
            for item in video_elements[:15]: # 拿前 15 个
                title_elem = item.query_selector("#video-title")
                if title_elem:
                    title = title_elem.inner_text().strip()
                    url = "https://www.youtube.com" + title_elem.get_attribute("href")
                    results.append({"title": title, "url": url})
            
            browser.close()
            return results
        except Exception as e:
            print(f"❌ 刷视频失败: {e}")
            browser.close()
            return []

if __name__ == "__main__":
    videos = brush_trending_videos()
    if videos:
        print("\n🏆 成功刷出视频列表：")
        for i, v in enumerate(videos, 1):
            print(f"{i}. {v['title']}")
            print(f"   URL: {v['url']}")
    else:
        print("\n⚠️ 未能刷出视频，请检查网络或代理。")

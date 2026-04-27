# -*- coding: utf-8 -*-
from playwright.sync_api import sync_playwright
import time

def get_trending_videos():
    print("[BrowserSniffer] 正在启动无头浏览器...")
    with sync_playwright() as p:
        # 启动 Chromium，headless=True 表示无界面运行
        browser = p.chromium.launch(headless=True)
        # 配置代理 (Playwright 这里的代理配置非常优雅)
        context = browser.new_context(
            proxy={"server": "http://127.0.0.1:7890"}
        )
        page = context.new_page()
        
        print("[BrowserSniffer] 正在访问 YouTube Trending...")
        try:
            page.goto("https://www.youtube.com/feed/trending", timeout=60000)
            # 等待视频列表加载完成
            page.wait_for_selector("ytd-video-renderer", timeout=30000)
            
            # 模拟一点滚动动作，确保动态元素渲染
            page.mouse.wheel(0, 1000)
            time.sleep(2)
            
            # 抓取前 10 个视频的链接
            video_links = page.query_selector_all("ytd-video-renderer a#video-title")
            
            results = []
            for link in video_links[:10]:
                title = link.get_attribute("title")
                url = "https://www.youtube.com" + link.get_attribute("href")
                results.append({"title": title, "url": url})
                
            browser.close()
            return results
        except Exception as e:
            print(f"  [Error] 浏览器探测失败: {e}")
            browser.close()
            return []

if __name__ == "__main__":
    videos = get_trending_videos()
    print(f"\n✅ 浏览器实时抓取到 {len(videos)} 条当前趋势视频：")
    for v in videos:
        print(f"- {v['title']} ({v['url']})")

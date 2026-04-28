# -*- coding: utf-8 -*-
from playwright.sync_api import sync_playwright
import time
import os

def explicit_browser_test():
    print("[Browser] 正在启动显性浏览器 (窗口即将弹出)...")
    with sync_playwright() as p:
        # headless=False 启动有界面的浏览器
        # slow_mo=500 减慢操作速度，方便观察
        browser = p.chromium.launch(headless=False, slow_mo=500)
        
        # 模拟真实的浏览器环境
        context = browser.new_context(
            viewport={'width': 1280, 'height': 800},
            proxy={"server": "http://127.0.0.1:7890"}
        )
        page = context.new_page()
        
        print("[Browser] 正在导航至 YouTube Trending...")
        try:
            # 访问首页
            page.goto("https://www.youtube.com/feed/trending", wait_until="networkidle", timeout=90000)
            
            # 强制等待几秒确保动态加载
            time.sleep(5)
            
            # 截图保存，让我们看看它看到了什么
            screenshot_path = r"E:\VideoTranslator_Project\youtube_trending.png"
            page.screenshot(path=screenshot_path)
            print(f"✅ 截图已保存至: {screenshot_path}")
            
            # 打印标题
            print(f"页面标题: {page.title()}")
            
            # 尝试抓取第一个视频标题
            first_video = page.locator("ytd-video-renderer #video-title").first
            if first_video.is_visible():
                print(f"探测到首个热点视频: {first_video.inner_text()}")
            
            print("[Browser] 测试完成，窗口将在 3 秒后关闭...")
            time.sleep(3)
            browser.close()
        except Exception as e:
            print(f"❌ 浏览器执行出错: {e}")
            # 出错也截个图，看看死在哪里了
            page.screenshot(path=r"E:\VideoTranslator_Project\browser_error.png")
            browser.close()

if __name__ == "__main__":
    explicit_browser_test()

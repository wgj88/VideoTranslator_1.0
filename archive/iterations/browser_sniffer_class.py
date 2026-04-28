# -*- coding: utf-8 -*-
from playwright.sync_api import sync_playwright
import time, random

class BrowserSniffer:
    def __init__(self):
        self.proxy = "http://127.0.0.1:7890"

    def sniff(self):
        print("[BrowserSniffer] 正在通过无头浏览器进行随机刷新刷榜...")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(proxy={"server": self.proxy})
            page = context.new_page()
            
            # 随机选择入口：要么是 Trending，要么是随机关键词的搜索结果页
            if random.random() > 0.5:
                url = "https://www.youtube.com/feed/trending"
            else:
                queries = ["futuristic tech", "hidden facts", "new inventions"]
                url = f"https://www.youtube.com/results?search_query={random.choice(queries)}"
            
            try:
                page.goto(url, wait_until="networkidle", timeout=60000)
                
                # 随机刷新：随机滚动不同的深度
                scroll_times = random.randint(2, 5)
                for _ in range(scroll_times):
                    page.mouse.wheel(0, random.randint(500, 1500))
                    time.sleep(random.uniform(0.5, 2.0)) # 随机停顿，模拟真人
                
                links = page.eval_on_selector_all("a", "elements => elements.map(e => ({href: e.href, text: e.innerText}))")
                
                video_list = []
                seen = set()
                for l in links:
                    if "/watch?v=" in l['href'] and l['text'].strip() and l['href'] not in seen:
                        video_list.append({"title": l['text'].replace("\n", " "), "url": l['href']})
                        seen.add(l['href'])
                
                browser.close()
                return video_list
            except:
                browser.close()
                return []

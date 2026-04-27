# -*- coding: utf-8 -*-
from playwright.sync_api import sync_playwright
import time

def ultimate_brush():
    print("[Browser] 启动终极嗅探模式...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(proxy={"server": "http://127.0.0.1:7890"})
        page = context.new_page()
        
        url = "https://www.youtube.com/results?search_query=trending"
        print(f"[Browser] 访问: {url}")
        
        try:
            page.goto(url, wait_until="networkidle", timeout=60000)
            time.sleep(5)
            
            links = page.eval_on_selector_all("a", "elements => elements.map(e => ({href: e.href, text: e.innerText}))")
            
            video_list = []
            seen_urls = set()
            for l in links:
                if "/watch?v=" in l['href'] and l['text'].strip() and l['href'] not in seen_urls:
                    # 避免 f-string 报错
                    clean_text = l['text'].replace("\n", " ")
                    video_list.append({"text": clean_text, "href": l['href']})
                    seen_urls.add(l['href'])
            
            browser.close()
            return video_list
        except Exception as e:
            print(f"❌ 失败: {e}")
            browser.close()
            return []

if __name__ == "__main__":
    results = ultimate_brush()
    if results:
        print("\n🔥 终极模式成功刷出视频：")
        for i, r in enumerate(results[:10], 1):
            print(f"{i}. {r['text']}")
            print(f"   URL: {r['href']}")
    else:
        print("\n💀 依旧颗粒无收。")

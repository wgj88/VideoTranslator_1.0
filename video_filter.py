# -*- coding: utf-8 -*-
import os, json, subprocess, sys

class VideoFilter:
    def __init__(self, config_path=None):
        if config_path is None:
            # 自动定位到脚本所在目录的 config 文件
            base_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(base_dir, "config_filter.json")
            
        with open(config_path, 'r', encoding='utf-8-sig') as f:
            self.config = json.load(f)['filters']
        self.proxy = "http://127.0.0.1:7890"

    def get_video_info(self, url):
        print(f"[Filter] Detecting metadata for: {url}")
        cmd = [
            'yt-dlp', '--proxy', self.proxy,
            '--dump-json', '--no-download', '--flat-playlist',
            url
        ]
        try:
            # 强制使用 utf-8 捕获输出
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, encoding='utf-8')
            return json.loads(result.stdout)
        except Exception as e:
            print(f"  [Error] Failed to get metadata: {e}")
            return None

    def check(self, url):
        info = self.get_video_info(url)
        if not info: return False, None

        # 1. Duration check
        duration = info.get('duration', 0)
        d_cfg = self.config['duration']
        if not (d_cfg['min_seconds'] <= duration <= d_cfg['max_seconds']):
            print(f"  REJECTED: Duration {duration}s not in range.")
            return False, info

        # 2. View count check
        views = info.get('view_count', 0)
        if views < self.config['metrics'].get('min_view_count', 0):
            print(f"  REJECTED: View count {views} too low.")
            return False, info

        # 3. Keyword check
        title = info.get('title', '').lower()
        desc = info.get('description', '').lower()
        content = title + " " + desc
        
        includes = self.config['content'].get('include_keywords', [])
        if includes and not any(k.lower() in content for k in includes):
            print(f"  REJECTED: Core keywords missing.")
            return False, info
            
        excludes = self.config['content'].get('exclude_keywords', [])
        if any(k.lower() in content for k in excludes):
            print(f"  REJECTED: Found exclude keywords.")
            return False, info

        print(f"  PASSED: {info.get('title')}")
        return True, info

if __name__ == '__main__':
    vf = VideoFilter()
    test_url = "https://www.youtube.com/watch?v=0x-_OVyzfa0"
    passed, meta = vf.check(test_url)
    print(f'FINAL_RESULT: {"PASSED" if passed else "REJECTED"}')

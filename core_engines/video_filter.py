# -*- coding: utf-8 -*-
import os, sys, json, subprocess

class VideoFilter:
    def __init__(self, config_path=None):
        if config_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(base_dir, "config_filter.json")

        with open(config_path, 'r', encoding='utf-8-sig') as f:
            self.config = json.load(f)['filters']
        self.proxy = "http://127.0.0.1:7890"

    def get_video_info(self, url):
        print(f"[Filter] Detecting metadata for: {url}")
        cmd = [
            sys.executable, '-m', 'yt_dlp', '--proxy', self.proxy,
            '--dump-json', '--no-download', '--flat-playlist',
            url
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, encoding='utf-8-sig')
            return json.loads(result.stdout)
        except Exception as e:
            print(f"  [Error] Failed to get metadata: {e}")
            return None

    def check(self, url):
        info = self.get_video_info(url)
        if not info: return False, None

        # 1. 时长检查
        duration = info.get('duration', 0)
        d_cfg = self.config['duration']
        if not (d_cfg['min_seconds'] <= duration <= d_cfg['max_seconds']):
            print(f"  REJECTED: Duration {duration}s not in range.")
            return False, info

        # 2. 播放量检查
        views = info.get('view_count', 0)
        if views < self.config['metrics'].get('min_view_count', 0):
            print(f"  REJECTED: View count {views} too low.")
            return False, info

        # 3. 关键词过滤 (防 PPT 第一线)
        title = info.get('title', '').lower()
        desc = info.get('description', '').lower()
        uploader = info.get('uploader', '').lower()
        content = title + " " + desc + " " + uploader

        excludes = self.config['content'].get('exclude_keywords', [])
        for k in excludes:
            if k.lower() in content:
                print(f"  REJECTED: Detected PPT-like keyword: {k}")
                return False, info

        # 4. 视觉活跃度指纹分析 (防 PPT 核心逻辑)
        # 如果是静止图片，码率(vbr)会极低
        vbr = info.get('vbr') or 0
        if vbr > 0 and vbr < self.config.get('min_vbitrate_kbps', 150):
            print(f"  REJECTED: Low visual activity detected ({vbr} kbps). Likely a static image/PPT.")
            return False, info

        # 5. YouTube 自动标识检测
        if "Topic" in uploader:
             print(f"  REJECTED: Topic channel detected. Usually static content.")
             return False, info

        print(f"  PASSED: {info.get('title')}")
        return True, info

if __name__ == '__main__':
    vf = VideoFilter()
    test_url = "https://www.youtube.com/watch?v=0x-_OVyzfa0"
    passed, meta = vf.check(test_url)
    print(f'FINAL_RESULT: {"PASSED" if passed else "REJECTED"}')

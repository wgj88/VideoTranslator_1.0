# -*- coding: utf-8 -*-
import os, subprocess, sys

class VideoDownloader:
    def __init__(self, output_dir=None):
        if output_dir is None:
            # 自动定位到脚本所在目录的 raw_videos
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.output_dir = os.path.join(base_dir, "raw_videos")
        else:
            self.output_dir = output_dir
            
        self.proxy = "http://127.0.0.1:7890"
        os.makedirs(self.output_dir, exist_ok=True)

    def download(self, url):
        print(f"\n[Downloader] 正在下载视频至: {self.output_dir}")
        # 使用绝对路径模板
        output_template = os.path.join(self.output_dir, "%(title)s.%(ext)s")
        
        cmd = [
            sys.executable, "-m", "yt_dlp",
            "--proxy", self.proxy,
            "-f", "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "-o", output_template,
            "--no-mtime",
            url
        ]

        try:
            subprocess.run(cmd, check=True)
            print("✅ 下载成功！")
            return True
        except Exception as e:
            print(f"❌ 下载失败: {e}")
            return False

if __name__ == "__main__":
    print("Downloader 路径已修正为绝对路径模式。")

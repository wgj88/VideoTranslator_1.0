# -*- coding: utf-8 -*-
import os, subprocess, sys

class VideoDownloader:
    def __init__(self, output_dir=None):
        if output_dir is None:
            # 默认指向 E:\VideoTranslator_Project\raw_videos
            self.output_dir = r"E:\VideoTranslator_Project\raw_videos"
        else:
            self.output_dir = output_dir

        self.proxy = "http://127.0.0.1:7890"
        os.makedirs(self.output_dir, exist_ok=True)

    def download(self, url):
        print(f"\n[Downloader] 📥 启动全自动下载 (含字幕抓取) -> {self.output_dir}")
        output_template = os.path.join(self.output_dir, "%(title)s.%(ext)s")

        cmd = [
            sys.executable, "-m", "yt_dlp",
            "--proxy", self.proxy,
            "-f", "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "-o", output_template,
            "--no-mtime",
            # --- 字幕抓取核心参数 ---
            "--write-subs",           # 下载人工上传字幕
            "--write-auto-subs",      # 允许下载 ASR 自动生成字幕
            "--sub-lang", "en,.*",    # 优先下载英文，如果没有则下载全部可用语言
            "--convert-subs", "srt",  # 统一转换为 SRT 格式
            "--embed-subs",           # (可选) 同时嵌入视频
            url
        ]

        try:
            # 记录下载前的状态，用于寻找新生成的字幕文件
            subprocess.run(cmd, check=True)
            print("✅ 视频与字幕下载/转换成功！")
            return True
        except Exception as e:
            print(f"❌ 下载流程中断: {e}")
            return False

if __name__ == "__main__":
    dl = VideoDownloader()
    print("VideoDownloader (V2.0 字幕增强版) 已就绪")

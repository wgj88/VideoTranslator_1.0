# -*- coding: utf-8 -*-
import os, sys, json, subprocess, random

class TrendSniffer:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), "config_sniffer.json")
        with open(config_path, "r", encoding="utf-8-sig") as f:
            self.config = json.load(f)["sniffer_settings"]
        self.proxy = "http://127.0.0.1:7890"

    def generate_random_query(self):
        """
        生成带有随机指纹的搜索词
        """
        seed = random.choice(self.config["seeds"])
        modifier = random.choice(self.config["modifiers"])
        # 30% 概率加入年份，20% 概率加入 "new"
        query = f"{modifier} {seed}"
        if random.random() < 0.4: query += f" {random.choice(['2026', 'review', 'vlog'])}"
        return query

    def sniff(self):
        all_candidate_urls = set()
        
        for _ in range(self.config["max_probes"]):
            query = self.generate_random_query()
            print(f"[Sniffer] 🎲 随机刷新探测领域: {query}")
            
            # 随机切换排序方式
            sort_method = random.choice(["relevance", "date", "rating", "view_count"])
            
            search_query = f"ytsearch{self.config['results_per_probe']}:{query}"
            cmd = [
                sys.executable, '-m', 'yt_dlp', '--proxy', self.proxy,
                '--get-id', '--flat-playlist',
                '--match-filter', "duration > 30 & duration < 900",
                search_query
            ]
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                video_ids = result.stdout.strip().split('\n')
                for vid in video_ids:
                    if vid and len(vid) < 15:
                        all_candidate_urls.add(f"https://www.youtube.com/watch?v={vid}")
            except:
                pass

        return list(all_candidate_urls)

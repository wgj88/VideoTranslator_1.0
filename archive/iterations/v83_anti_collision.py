# -*- coding: utf-8 -*-
import os, sys, json, subprocess, time, threading, queue
import numpy as np
import soundfile as sf
import whisper

# --- 物理资产配置 ---
FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

sys.path.append(r"E:\VideoTranslator_Project")
from clone_dubber import VideoCloneDubber

class AntiCollisionFactory:
    def __init__(self):
        print("\n" + "🛡️"*10 + " V83 防撞对齐引擎启动 " + "🛡️"*10)
        self.db = VideoCloneDubber()
        self.auditor = whisper.load_model("base")
        self.task_queue = queue.Queue()
        self.results = []
        self.is_done = False
        self.temp_dir = r"E:\VideoTranslator_Project\temp_factory\v83_run"
        os.makedirs(self.temp_dir, exist_ok=True)

    def process_and_squeeze(self, idx, raw_p, start_t, next_start_t):
        """核心防撞：物理测量并执行弹性挤压"""
        # 1. 纳米级熔断 (V77)
        res = self.auditor.transcribe(raw_p, word_timestamps=True)
        semantic_end = res['segments'][-1]['end'] if res['segments'] else 0
        
        # 2. 计算可用空隙 (Available Gap)
        # 我们要求在下一句开始前 50ms 必须彻底安静
        available_gap = next_start_t - start_t - 0.05
        
        final_p = os.path.join(self.temp_dir, f"v83_final_{idx}.wav")
        
        # 3. 判定是否需要挤压
        if semantic_end > available_gap:
            # 自动计算语速倍率
            tempo = semantic_end / available_gap
            print(f"  🚨 [Collision!] 第 {idx+1} 段溢出 {semantic_end - available_gap:.2f}s，正在执行 {tempo:.2f}x 弹性挤压...")
            cmd = [
                FFMPEG_BIN, "-y", "-i", raw_p,
                "-af", f"atrim=end={semantic_end},asetpts=PTS-STARTPTS,atempo={tempo},afade=t=out:st={available_gap-0.05}:d=0.05",
                final_p
            ]
        else:
            # 安全状态
            cmd = [
                FFMPEG_BIN, "-y", "-i", raw_p,
                "-af", f"atrim=end={semantic_end},asetpts=PTS-STARTPTS,afade=t=out:st={semantic_end-0.05}:d=0.05",
                final_p
            ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        return final_p

    def run_1min_production(self, script_p, seed_wav):
        with open(script_p, "r", encoding="utf-8") as f: data = json.load(f)
        data = [it for it in data if it['start'] < 60]
        
        start_time = time.time()
        for i, item in enumerate(data):
            # GPU 推理
            wav = self.db.model.generate(text=item['zh'], reference_wav_path=seed_wav, inference_timesteps=20)
            raw_p = os.path.join(self.temp_dir, f"raw_{i}.wav")
            sf.write(raw_p, wav, self.db.sample_rate)
            
            # 物理防撞处理 (串行处理以保证 next_start_t 的引用)
            next_start_t = data[i+1]['start'] if i < len(data)-1 else item['end']
            processed_p = self.process_and_squeeze(i, raw_p, item['start'], next_start_t)
            self.results.append((processed_p, item['start']))
            print(f"  -> [{i+1}/13] 已完成防撞对齐。")

        print(f"\n🏆 V83 核心生成完成！总耗时: {time.time() - start_time:.2f}s")
        return sorted(self.results, key=lambda x: x[1])

if __name__ == "__main__":
    factory = AntiCollisionFactory()
    script = r"E:\VideoTranslator_Project\unhinged_tech\V81_60S_FIXED.json"
    seed = r"E:\VideoTranslator_Project\unhinged_tech\seeds\ultra_pure_seed.wav"
    results = factory.run_1min_production(script, seed)

    # 封装最终 MP4
    output_mp4 = r"E:\VideoTranslator_Project\output_final\V83_NO_OVERLAP_FLAGSHIP.mp4"
    temp_zh = r"E:\VideoTranslator_Project\unhinged_tech\v83_zh_clean.wav"
    
    # 物理缝合
    input_args = []
    filter_parts = []
    for idx, (p, start_t) in enumerate(results):
        input_args.extend(["-i", p])
        filter_parts.append(f"[{idx}:a]adelay={int(start_t*1000)}|{int(start_t*1000)}[a{idx}]")
    mix_zh = "".join([f"[a{k}]" for k in range(len(results))]) + f"amix=inputs={len(results)}"
    subprocess.run([FFMPEG_BIN, "-y"] + input_args + ["-filter_complex", ";".join(filter_parts) + ";" + mix_zh, temp_zh], check=True)

    # 视频合成
    raw_v = r"E:\VideoTranslator_Project\raw_videos\The unhinged world of tech in 2026....f399.mp4"
    bgm = r"E:\VideoTranslator_Project\unhinged_tech\separated\other.wav"
    cmd_pack = [
        FFMPEG_BIN, "-y", "-ss", "0", "-t", "60", "-i", raw_v, "-i", temp_zh, "-ss", "0", "-t", "60", "-i", bgm,
        "-filter_complex", "[1:a]volume=1.4[zh];[2:a]volume=0.15[bg];[zh][bg]amix=inputs=2:duration=first[out];[0:v]subtitles='E\\:/VideoTranslator_Project/unhinged_tech/v81_final.srt':force_style='FontSize=20,PrimaryColour=&H00FFFF,BorderStyle=1,Outline=1,Alignment=2'[v_sub]",
        "-map", "[v_sub]", "-map", "[out]", "-c:v", "libx264", "-c:a", "aac", output_mp4
    ]
    subprocess.run(cmd_pack, check=True)
    print(f"\n🏁 V83 零重合成片已诞生：{output_mp4}")

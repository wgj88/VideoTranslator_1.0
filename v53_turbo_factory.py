# -*- coding: utf-8 -*-
import os, sys, json, subprocess, whisper, time, threading, queue
import numpy as np
import soundfile as sf

# --- 路径注入 ---
FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

sys.path.append(r"E:\VideoTranslator_Project")
from clone_dubber import VideoCloneDubber

class TurboFactory:
    def __init__(self):
        print("\n" + "⚡"*10 + " V53 闪电量产引擎启动 " + "⚡"*10)
        self.db = VideoCloneDubber()
        # 1. 采用 tiny 模型作为轻量化审计官
        self.auditor = whisper.load_model("tiny")
        self.audit_queue = queue.Queue()
        self.results = []
        self.is_done = False
        self.temp_dir = r"E:\VideoTranslator_Project\temp_factory\turbo_run"
        os.makedirs(self.temp_dir, exist_ok=True)

    def audit_worker(self):
        """异步审计工作线程：负责回听并执行物理微操"""
        while not self.is_done or not self.audit_queue.empty():
            try:
                task = self.audit_queue.get(timeout=1)
                idx, raw_p, item, duration = task
                
                # 执行轻量化审计 (tiny 模型几乎瞬发)
                res = self.auditor.transcribe(raw_p, verbose=False)
                last_end = res['segments'][-1]['end'] if res['segments'] else duration
                
                # 物理保全手术 (V52.1 逻辑)
                final_p = os.path.join(self.temp_dir, f"turbo_fixed_{idx}.wav")
                protected_end = last_end + 0.2
                subprocess.run([
                    FFMPEG_BIN, "-y", "-i", raw_p,
                    "-af", f"atrim=end={protected_end},asetpts=PTS-STARTPTS,afade=t=out:st={last_end}:d=0.2",
                    final_p
                ], capture_output=True)
                
                self.results.append((final_p, item['start']))
                print(f"  [ASR-Check] 片段 {idx+1} 审计完成。")
                self.audit_queue.task_done()
            except queue.Empty:
                continue

    def run_production(self, script_path, seed_wav):
        with open(script_path, "r", encoding="utf-8") as f: data = json.load(f)
        
        # 启动异步审计线程
        t = threading.Thread(target=self.audit_worker)
        t.start()

        start_time = time.time()
        print(f"\n[Turbo] 正在全速生成音频流 (并发模式)...")

        for i, item in enumerate(data):
            # 2. GPU 专注生成
            text = item['zh'].strip() + "。"
            wav = self.db.model.generate(text=text, reference_wav_path=seed_wav, inference_timesteps=20)
            
            raw_p = os.path.join(self.temp_dir, f"raw_{i}.wav")
            sf.write(raw_p, wav, self.db.sample_rate)
            
            # 3. 立即派发审计任务，主线程不做停留，直接去写下一句
            self.audit_queue.put((i, raw_p, item, len(wav)/self.db.sample_rate))
            print(f"  [Generator] 片段 {i+1}/{len(data)} 已交付。")

        self.is_done = True
        t.join()
        
        end_time = time.time()
        print(f"\n🏆 闪电渲染完成！耗时: {end_time - start_time:.2f}秒")
        return sorted(self.results, key=lambda x: x[1])

if __name__ == "__main__":
    tf = TurboFactory()
    script = r"E:\VideoTranslator_Project\separated_audio\V51_CALIBRATED_SCRIPT.json"
    role_lib = r"E:\VideoTranslator_Project\temp_factory\v9_role_library.json"
    import json
    with open(role_lib, "r") as f: seed = json.load(f)['SPEAKER_00']['wav']
    
    tf.run_production(script, seed)

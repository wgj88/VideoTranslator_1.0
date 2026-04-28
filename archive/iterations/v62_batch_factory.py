# -*- coding: utf-8 -*-
import os, sys, json, subprocess, whisper, time, threading, queue
import numpy as np
import soundfile as sf

# --- 物理路径锁定 ---
FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

sys.path.append(r"E:\VideoTranslator_Project")
from clone_dubber import VideoCloneDubber

class BatchTurboFactory:
    def __init__(self, batch_size=4):
        print("\n" + "🚀"*10 + f" V62 批处理量产引擎启动 (Batch Size: {batch_size}) " + "🚀"*10)
        self.db = VideoCloneDubber()
        self.auditor = whisper.load_model("tiny")
        self.batch_size = batch_size
        self.audit_queue = queue.Queue()
        self.results = []
        self.temp_dir = r"E:\VideoTranslator_Project\temp_factory\batch_run"
        os.makedirs(self.temp_dir, exist_ok=True)

    def audit_worker(self):
        while True:
            task = self.audit_queue.get()
            if task is None: break
            idx, raw_p, start_t, duration = task
            
            # 极速审计
            res = self.auditor.transcribe(raw_p, verbose=False)
            last_end = res['segments'][-1]['end'] if res['segments'] else duration
            
            final_p = os.path.join(self.temp_dir, f"fixed_{idx}.wav")
            subprocess.run([
                FFMPEG_BIN, "-y", "-i", raw_p,
                "-af", f"atrim=end={last_end + 0.2},asetpts=PTS-STARTPTS,afade=t=out:st={last_end}:d=0.2",
                final_p
            ], capture_output=True)
            
            self.results.append((final_p, start_t))
            self.audit_queue.task_done()

    def run_production(self, script_path, seed_wav):
        with open(script_path, "r", encoding="utf-8") as f: data = json.load(f)
        
        # 启动后台审计
        audit_thread = threading.Thread(target=self.audit_worker)
        audit_thread.start()

        start_time = time.time()
        
        # 3. 核心批处理逻辑：分块生成
        for i in range(0, len(data), self.batch_size):
            batch = data[i:i+self.batch_size]
            texts = [item['zh'].strip() + "。" for item in batch]
            
            print(f"\n[GPU-Batch] 正在并行产出第 {i+1} 至 {min(i+self.batch_size, len(data))} 段音频...")
            
            # 这里调用底层的 batch 生成逻辑 (如果模型支持 native batch)
            # 目前采用极速并发模拟或批量调用
            for sub_idx, text in enumerate(texts):
                global_idx = i + sub_idx
                # 生产
                wav = self.db.model.generate(text=text, reference_wav_path=seed_wav, inference_timesteps=20)
                raw_p = os.path.join(self.temp_dir, f"raw_{global_idx}.wav")
                sf.write(raw_p, wav, self.db.sample_rate)
                
                # 派发异步审计
                self.audit_queue.put((global_idx, raw_p, batch[sub_idx]['start'], len(wav)/self.db.sample_rate))

        self.audit_queue.join()
        self.audit_queue.put(None)
        audit_thread.join()
        
        print(f"\n🏆 批处理生产完成！总耗时: {time.time() - start_time:.2f}s")
        return sorted(self.results, key=lambda x: x[1])

if __name__ == "__main__":
    bf = BatchTurboFactory(batch_size=4) # Blackwell 建议开启 4-8 并发
    script = r"E:\VideoTranslator_Project\separated_audio\V51_CALIBRATED_SCRIPT.json"
    role_lib = r"E:\VideoTranslator_Project\temp_factory\v9_role_library.json"
    import json
    with open(role_lib, "r") as f: seed = json.load(f)['SPEAKER_00']['wav']
    bf.run_production(script, seed)

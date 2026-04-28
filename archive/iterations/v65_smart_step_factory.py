# -*- coding: utf-8 -*-
import os, sys, json, time, threading, queue
import soundfile as sf
import librosa

sys.path.append(r"E:\VideoTranslator_Project")
from v64_batch_factory import FullBatchSentinelFactory

class SmartStepFactory(FullBatchSentinelFactory):
    def get_smart_steps(self, text):
        """核心算力调度逻辑"""
        count = len(text)
        if count <= 6: return 10    # 短句：极速
        if count <= 25: return 20   # 中句：标准
        return 45                    # 长句：发烧级

    def run_production(self, script_path, seed_wav):
        with open(script_path, "r", encoding="utf-8") as f: data = json.load(f)
        t = threading.Thread(target=self.sentinel_worker)
        t.start()
        
        start_time = time.time()
        print("\n[V65-Smart] 智能算力调度开启...")

        for i, item in enumerate(data):
            text = item['zh'].strip()
            # 动态分配步数
            steps = self.get_smart_steps(text)
            
            # 生成
            wav = self.db.model.generate(text=text+"。", reference_wav_path=seed_wav, inference_timesteps=steps)
            raw_p = os.path.join(self.temp_dir, f"raw_{i}.wav")
            sf.write(raw_p, wav, self.db.sample_rate)
            
            self.task_queue.put((i, raw_p, item['start']))
            print(f"  -> [{i+1}/{len(data)}] 字数:{len(text)} | 调度步数:{steps}")

        self.is_done = True
        t.join()
        print(f"\n🏆 智能调度渲染完成！耗时: {time.time() - start_time:.2f}s")
        return sorted(self.results, key=lambda x: x[1])

if __name__ == "__main__":
    factory = SmartStepFactory(batch_size=1) # 先用串行验证调度逻辑
    script = r"E:\VideoTranslator_Project\separated_audio\V51_CALIBRATED_SCRIPT.json"
    role_lib = r"E:\VideoTranslator_Project\temp_factory\v9_role_library.json"
    import json
    with open(role_lib, "r") as f: seed = json.load(f)['SPEAKER_00']['wav']
    factory.run_production(script, seed)

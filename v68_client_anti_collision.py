# -*- coding: utf-8 -*-
import os, sys, json, subprocess, time, requests, threading, queue
import librosa, soundfile as sf

FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

class AntiCollisionClient:
    def __init__(self, server_url="http://127.0.0.1:8000"):
        print("\n" + "🛡️"*10 + " V68 动态防撞流水线启动 " + "🛡️"*10)
        self.server_url = server_url
        self.temp_dir = r"E:\VideoTranslator_Project\temp_factory\v68_run"
        os.makedirs(self.temp_dir, exist_ok=True)
        self.results = []

    def run_safe_production(self, script_path, seed_wav):
        with open(script_path, "r", encoding="utf-8") as f: data = json.load(f)
        
        start_time = time.time()
        print(f"\n[V68] 正在执行“内容感知”动态排期...")

        for i, item in enumerate(data):
            text = item['zh'].strip()
            raw_save_path = os.path.join(self.temp_dir, f"raw_{i}.wav")
            
            # 1. 初始生成 (1.0x)
            payload = {"text": text+"。", "ref_wav": seed_wav, "steps": 25, "save_path": raw_save_path}
            r = requests.post(f"{self.server_url}/generate", json=payload, timeout=60, proxies={"http": None, "https": None}).json()
            
            # 2. 物理碰撞检测
            y, sr = sf.read(raw_save_path)
            intervals = librosa.effects.split(y, top_db=25)
            actual_end = intervals[-1][1]/sr if len(intervals)>0 else len(y)/sr
            
            # 计算可用空间：直到下一句开口前的时间
            if i < len(data) - 1:
                available_space = data[i+1]['start'] - item['start']
            else:
                available_space = 10.0 # 最后一句给足空间
            
            # 3. 动态调速 (Anti-Collision)
            # 如果音频比空间长，或者离下一句太近 (<0.1s)，则加速
            target_dur = available_space - 0.1 # 预留 100ms 强制间隔
            tempo = 1.0
            if actual_end > target_dur:
                tempo = actual_end / target_dur
                print(f"  ⚠️ [碰撞预警] 片段 {i+1} 空间紧张，动态调速至 {tempo:.2f}x")
            
            # 4. 执行最终物理对齐
            final_p = os.path.join(self.temp_dir, f"v68_fixed_{i}.wav")
            # 使用 atempo 物理压缩
            cmd = [
                FFMPEG_BIN, "-y", "-i", raw_save_path,
                "-af", f"atrim=end={actual_end+0.1},asetpts=PTS-STARTPTS,atempo={tempo},afade=t=out:st={max(0, actual_end/tempo-0.1)}:d=0.1",
                final_p
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            self.results.append((final_p, item['start']))
            print(f"  -> [{i+1}/{len(data)}] 状态: OK | 语速: {tempo:.2f}x | 文字: {text[:15]}")

        print(f"\n🏆 前 10 句防撞渲染完成！耗时: {time.time() - start_time:.2f}s")
        # 执行快速合并供审阅
        test_wav = r"E:\VideoTranslator_Project\output_final\V68_ANTI_COLLISION_AUDIT.wav"
        input_args = []
        filter_parts = []
        for idx, (p, st) in enumerate(self.results):
            input_args.extend(["-i", p])
            delay = int(st * 1000)
            filter_parts.append(f"[{idx}:a]adelay={delay}|{delay}[a{idx}]")
        mix_str = "".join([f"[a{k}]" for k in range(len(self.results))]) + f"amix=inputs={len(self.results)}"
        subprocess.run([FFMPEG_BIN, "-y"] + input_args + ["-filter_complex", ";".join(filter_parts)+";"+mix_str, test_wav], check=True)
        print(f"📂 样片已就绪：{test_wav}")

if __name__ == "__main__":
    client = AntiCollisionClient()
    script = r"E:\VideoTranslator_Project\unhinged_tech\V68_NATURAL_SCRIPT.json"
    seed = r"E:\VideoTranslator_Project\unhinged_tech\seeds\ultra_pure_seed.wav"
    client.run_safe_production(script, seed)

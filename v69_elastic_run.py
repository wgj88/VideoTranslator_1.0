# -*- coding: utf-8 -*-
import os, sys, json, subprocess, time, requests
import librosa, soundfile as sf

# --- 物理资产配置 ---
FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

sys.path.append(r"E:\VideoTranslator_Project")
from v67_client_master import FinalV67Client

class ElasticSyncClient(FinalV67Client):
    def run_elastic_demo(self, script_path, seed_wav):
        with open(script_path, "r", encoding="utf-8") as f: data = json.load(f)
        start_time = time.time()
        print("\n" + "🛡️"*10 + " V69 弹性调速渲染启动 " + "🛡️"*10)

        for i, item in enumerate(data):
            text = item['zh'].strip()
            raw_p = os.path.join(self.temp_dir, f"v69_raw_{i}.wav")
            # 1. 调取常驻核心生成 (1.0x)
            payload = {"text": text+"。", "ref_wav": seed_wav, "steps": 30, "save_path": raw_p}
            requests.post(f"{self.server_url}/generate", json=payload, proxies={"http": None, "https": None})
            
            # 2. 测量物理长度
            y, sr = sf.read(raw_p)
            actual_dur = len(y)/sr
            expected_dur = item['end'] - item['start']
            
            # 3. 动态调速逻辑：弹性胀缩
            # 如果音频太长，加速；如果音频太短，减速（拖长音）
            tempo = actual_dur / expected_dur if expected_dur > 0.1 else 1.0
            
            # 安全阈值保护：减速不少于 0.8x，加速不超过 1.4x
            final_tempo = max(0.8, min(1.4, tempo))
            
            print(f"  -> [{i+1}] 物理:{actual_dur:.1f}s | 空间:{expected_dur:.1f}s | 最终调速:{final_tempo:.2f}x")
            
            final_p = os.path.join(self.temp_dir, f"v69_fixed_{i}.wav")
            # 4. FFmpeg 物理缩放
            cmd = [
                FFMPEG_BIN, "-y", "-i", raw_p,
                "-af", f"atempo={final_tempo},afade=t=out:st={max(0, actual_dur/final_tempo-0.1)}:d=0.1",
                final_p
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            self.results.append((final_p, item['start']))

        # 合成样片
        test_wav = r"E:\VideoTranslator_Project\output_final\V69_ELASTIC_FRONT_5_AUDIT.wav"
        input_args = []
        filter_parts = []
        for idx, (p, st) in enumerate(self.results):
            input_args.extend(["-i", p])
            filter_parts.append(f"[{idx}:a]adelay={int(st*1000)}|{int(st*1000)}[a{idx}]")
        mix_str = "".join([f"[a{k}]" for k in range(len(self.results))]) + f"amix=inputs={len(self.results)}"
        subprocess.run([FFMPEG_BIN, "-y"] + input_args + ["-filter_complex", ";".join(filter_parts)+";"+mix_str, test_wav], check=True)
        print(f"\n🏆 V69 弹性样片已产出：{test_wav}")

if __name__ == "__main__":
    client = ElasticSyncClient()
    client.run_elastic_demo(
        r"E:\VideoTranslator_Project\unhinged_tech\V69_ELASTIC_SCRIPT.json",
        r"E:\VideoTranslator_Project\unhinged_tech\seeds\ultra_pure_seed.wav"
    )

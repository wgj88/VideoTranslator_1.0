# -*- coding: utf-8 -*-
import os, sys, json, subprocess, time, requests, threading, queue
import librosa, soundfile as sf

FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]
os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""

def format_timestamp(seconds):
    td = float(seconds)
    return f"{int(td//3600):02d}:{int((td%3600)//60):02d}:{int(td%60):02d},{int((td%1)*1000):03d}"

class FinalV67Client:
    def __init__(self, server_url="http://127.0.0.1:8000"):
        print("\n" + "💎"*10 + " V67 旗舰版量产客户端启动 " + "💎"*10)
        self.server_url = server_url
        self.temp_dir = r"E:\VideoTranslator_Project\temp_factory\v67_run"
        os.makedirs(self.temp_dir, exist_ok=True)
        self.task_queue = queue.Queue()
        self.results = []
        self.is_done = False

    def get_smart_steps(self, text):
        count = len(text)
        if count <= 6: return 10
        if count <= 25: return 20
        return 45

    def sentinel_worker(self):
        while not self.is_done or not self.task_queue.empty():
            try:
                task = self.task_queue.get(timeout=1)
                idx, raw_p, start_t = task
                y, sr = sf.read(raw_p)
                intervals = librosa.effects.split(y, top_db=25)
                last_end = intervals[-1][1]/sr if len(intervals)>0 else len(y)/sr
                
                final_p = os.path.join(self.temp_dir, f"v67_fixed_{idx}.wav")
                subprocess.run([FFMPEG_BIN, "-y", "-i", raw_p, "-af", f"atrim=end={last_end+0.2},asetpts=PTS-STARTPTS,afade=t=out:st={last_end}:d=0.1", final_p], capture_output=True)
                self.results.append((final_p, start_t))
                self.task_queue.task_done()
            except queue.Empty: continue

    def run_full_production(self, script_path, seed_wav, raw_video, bgm_wav):
        with open(script_path, "r", encoding="utf-8") as f: data = json.load(f)
        
        t = threading.Thread(target=self.sentinel_worker)
        t.start()

        start_time = time.time()
        print(f"\n[Client] 正在通过常驻核心执行全量产...")

        for i, item in enumerate(data):
            text = item['zh'].strip()
            save_path = os.path.join(self.temp_dir, f"raw_{i}.wav")
            
            payload = {"text": text+"。", "ref_wav": seed_wav, "steps": self.get_smart_steps(text), "save_path": save_path}
            for retry in range(5):
                try:
                    r = requests.post(f"{self.server_url}/generate", json=payload, timeout=60, proxies={"http": None, "https": None}).json()
                    self.task_queue.put((i, save_path, item['start']))
                    print(f"  -> [{i+1}/{len(data)}] 渲染成功 (调配步数:{payload['steps']} | 耗时:{r.get('duration', 0):.2f}s)")
                    break
                except Exception as e:
                    print(f"  ⚠️ 请求重试: {e}")
                    time.sleep(2)

        self.is_done = True
        t.join()
        
        sorted_res = sorted(self.results, key=lambda x: x[1])
        
        print("\n[Client] 正在执行全篇物理级合成...")
        temp_zh_track = os.path.join(self.temp_dir, "v67_zh_full.wav")
        input_args = []
        filter_parts = []
        for idx, (p, start_t) in enumerate(sorted_res):
            input_args.extend(["-i", p])
            delay = int(start_t * 1000)
            filter_parts.append(f"[{idx}:a]adelay={delay}|{delay}[a{idx}]")
            
        mix_str = "".join([f"[a{k}]" for k in range(len(sorted_res))]) + f"amix=inputs={len(sorted_res)}:duration=longest,volume={len(sorted_res)}"
        
        with open(os.path.join(self.temp_dir, "mix_filter.txt"), "w") as f:
            f.write(";".join(filter_parts) + ";" + mix_str)
            
        subprocess.run([FFMPEG_BIN, "-y"] + input_args + ["-filter_complex_script", os.path.join(self.temp_dir, "mix_filter.txt"), temp_zh_track], check=True)

        print("\n[Client] 正在生成同步字幕 (SRT)...")
        srt_p = os.path.join(self.temp_dir, "v67_subtitles.srt")
        with open(srt_p, "w", encoding="utf-8") as f:
            for i, item in enumerate(data):
                f.write(f"{i+1}\n{format_timestamp(item['start'])} --> {format_timestamp(item['end'])}\n{item['zh']}\n\n")

        print("\n[Master] 正在压制最终商业母带 (NVENC 极速硬件编码)...")
        output_mp4 = r"E:\VideoTranslator_Project\output_final\V67_UNHINGED_ULTIMATE_MASTER_WITH_SUB.mp4"
        escaped_srt = srt_p.replace("\\", "/").replace(":", "\\:")
        
        cmd_pack = [
            FFMPEG_BIN, "-y", "-i", raw_video, "-i", temp_zh_track, "-i", bgm_wav,
            "-filter_complex", f"[1:a]volume=1.4[zh];[2:a]volume=0.15[bg];[zh][bg]amix=inputs=2:duration=first[out];[0:v]subtitles='{escaped_srt}':force_style='FontSize=20,PrimaryColour=&H00FFFF,BorderStyle=1,Outline=1,Alignment=2'[v_sub]",
            "-map", "[v_sub]", "-map", "[out]", "-c:v", "h264_nvenc", "-preset", "p4", "-cq", "22", "-c:a", "aac", output_mp4
        ]
        subprocess.run(cmd_pack, check=True)
        print(f"\n🏆 九分钟全长带字幕母带已交付！总耗时: {time.time() - start_time:.2f}s")
        print(f"📂 文件路径: {output_mp4}")

if __name__ == "__main__":
    client = FinalV67Client()
    script = r"E:\VideoTranslator_Project\unhinged_tech\UNHINGED_FINAL_506_SCRIPT.json"
    seed = r"E:\VideoTranslator_Project\unhinged_tech\seeds\ultra_pure_seed.wav"
    video = r"E:\VideoTranslator_Project\raw_videos\The unhinged world of tech in 2026....f399.mp4"
    bgm = r"E:\VideoTranslator_Project\unhinged_tech\separated\other.wav"
    client.run_full_production(script, seed, video, bgm)

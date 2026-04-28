# -*- coding: utf-8 -*-
import os, sys, json, subprocess, re, time
import numpy as np
import soundfile as sf
import whisper

# --- 暴力路径锁定 (RTX 5060 Ti Blackwell 专修) ---
FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
FFMPEG_DIR = os.path.dirname(FFMPEG_BIN)
os.environ["PATH"] = FFMPEG_DIR + os.pathsep + os.environ["PATH"]

PROJECT_ROOT = r"E:\VideoTranslator_Project"
sys.path.append(PROJECT_ROOT)
from clone_dubber import VideoCloneDubber

class IntelligentFactory:
    def __init__(self):
        print("\n" + "🚀"*10 + " AI 汉化工厂 v2.0 (终极稳定版) 启动 " + "🚀"*10)
        self.db = VideoCloneDubber()
        self.auditor = whisper.load_model("base")

    def run_production(self, script_json, video_file, bgm_file, role_lib_p):
        with open(script_json, "r", encoding="utf-8") as f: data = json.load(f)
        with open(role_lib_p, "r", encoding="utf-8") as f: role_lib = json.load(f)
        
        temp_run_dir = os.path.join(PROJECT_ROOT, "factory_v2_run")
        os.makedirs(temp_run_dir, exist_ok=True)

        processed_segments = []
        for i, item in enumerate(data):
            zh_text = item['zh'].strip()
            spk = item.get('speaker', 'SPEAKER_00')
            seed = role_lib.get(spk)
            
            # --- 智慧导演逻辑 ---
            # 1. 自动锚定：短句加垫词防崩
            is_short = len(zh_text) < 4 or (item['end'] - item['start'] < 1.2)
            final_text = f"好的。{zh_text}。" if is_short else f"{zh_text}。"
            
            # 2. 情感监测：！感叹号自动降温
            is_emotional = "！" in zh_text or any(k in zh_text for k in ["哇", "看呐", "天啊"])
            cfg = 1.2 if is_emotional else 2.0
            
            print(f"  -> [{i+1}/{len(data)}] {'[🔥惊叹]' if is_emotional else ''}{'[⚓短句]' if is_short else ''} 渲染: {zh_text[:12]}...")

            # 渲染 (30-Step 兼顾品质与速度)
            wav = self.db.model.generate(text=final_text, reference_wav_path=seed['wav'], inference_timesteps=30, cfg_value=cfg)
            raw_p = os.path.join(temp_run_dir, f"raw_{i}.wav")
            sf.write(raw_p, wav, self.db.sample_rate)

            # 3. AI 手术定位 (精确剥离垫词)
            res = self.auditor.transcribe(raw_p, word_timestamps=True)
            
            start_t = 0.0
            if is_short and res['segments']:
                words = []
                for s in res['segments']: words.extend(s.get('words', []))
                # 跳过“好的”对应的单词 (通常前2个)
                if len(words) > 2: start_t = words[2]['start']
                elif len(words) > 0: start_t = words[0]['end']
            elif res['segments']:
                start_t = res['segments'][0]['start']

            expected_dur = item['end'] - item['start']
            end_t = res['segments'][-1]['end'] if res['segments'] else (start_t + expected_dur)
            
            # 4. 自动语速自适应
            actual_content_dur = end_t - start_t
            tempo = max(0.5, min(2.0, actual_content_dur / expected_dur)) if expected_dur > 0.1 else 1.0
            
            # 5. 自动音高对齐 (惊叹句降调 3%)
            pitch_filter = "rubberband=pitch=0.97," if is_emotional else ""
            
            final_seg_p = os.path.join(temp_run_dir, f"v2_seg_{i}.wav")
            cmd = [
                FFMPEG_BIN, "-y", "-i", raw_p,
                "-af", f"atrim=start={start_t},asetpts=PTS-STARTPTS,{pitch_filter}atempo={tempo},afade=t=in:d=0.05,afade=t=out:st={max(0, expected_dur-0.1)}:d=0.1",
                final_seg_p
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            processed_segments.append((final_seg_p, item['start']))

        # 6. 总合成
        print("\n[Composer] 正在执行全篇物理级合成...")
        temp_zh_track = os.path.join(temp_run_dir, "v2_zh_full.wav")
        input_args = []
        filter_parts = []
        for idx, (p, start) in enumerate(processed_segments):
            input_args.extend(["-i", p])
            delay = int(start * 1000)
            filter_parts.append(f"[{idx}:a]adelay={delay}|{delay}[a{idx}]")
        
        mix_str = "".join([f"[a{k}]" for k in range(len(processed_segments))]) + f"amix=inputs={len(processed_segments)}:duration=longest,volume={len(processed_segments)}"
        subprocess.run([FFMPEG_BIN, "-y"] + input_args + ["-filter_complex", ";".join(filter_parts) + ";" + mix_str, temp_zh_track], check=True, capture_output=True)

        output_video = os.path.join(PROJECT_ROOT, "output_final", "V48_SMART_AUTOMATED_MASTER.mp4")
        subprocess.run([
            FFMPEG_BIN, "-y", "-i", video_file, "-i", temp_zh_track, "-i", bgm_file,
            "-filter_complex", "[1:a]volume=1.4[zh];[2:a]volume=0.15[bg];[zh][bg]amix=inputs=2:duration=first[out]",
            "-map", "0:v", "-map", "[out]", "-c:v", "copy", "-c:a", "aac", output_video
        ], check=True)
        print(f"\n🏆 全自动 V2.0 运行圆满成功！成品：{output_video}")

if __name__ == "__main__":
    script = r"E:\VideoTranslator_Project\separated_audio\V45_QUOTA_SCRIPT.json"
    video = r"E:\VideoTranslator_Project\raw_videos\Vlog ｜ New technology paves way for better life at CICPE.mp4"
    bgm = r"C:\Users\Administrator\separated_audio\pure_bgm.wav"
    role_lib = r"E:\VideoTranslator_Project\temp_factory\v9_role_library.json"
    
    factory = IntelligentFactory()
    factory.run_production(script, video, bgm, role_lib)

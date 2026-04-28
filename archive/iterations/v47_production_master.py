# -*- coding: utf-8 -*-
import os, sys, json, subprocess, whisper, time, numpy as np
import soundfile as sf
import requests

# --- 物理资产配置 ---
FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

sys.path.append(r"E:\VideoTranslator_Project")
from clone_dubber import VideoCloneDubber

class AgenticFactory:
    def __init__(self, api_key):
        self.db = VideoCloneDubber()
        self.auditor = whisper.load_model("base")
        self.api_key = api_key
        self.headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        self.temp_dir = r"E:\VideoTranslator_Project\temp_factory\agent_run"
        os.makedirs(self.temp_dir, exist_ok=True)

    def _get_llm_fix(self, text, error_type, duration):
        """调用 LLM 导演进行台词自愈"""
        prompt = f"""【台词修复任务】
原始台词：{text}
错误：{error_type} (时限 {duration:.2f}s)
要求：重写台词，确保语气极其平稳（禁止感叹词），字数严格适配时限。
返回JSON: {{"fixed_zh": "..."}}
"""
        payload = {"model": "deepseek-ai/DeepSeek-V3", "messages": [{"role": "user", "content": prompt}], "response_format": {"type": "json_object"}}
        try:
            r = requests.post("https://api.siliconflow.cn/v1/chat/completions", json=payload, headers=self.headers, timeout=20).json()
            return json.loads(r['choices'][0]['message']['content'])['fixed_zh']
        except: return text

    def process_with_self_healing(self, script_path, role_lib_p, output_wav):
        with open(script_path, "r", encoding="utf-8") as f: data = json.load(f)
        with open(role_lib_p, "r", encoding="utf-8") as f: role_lib = json.load(f)
        
        seed_wav = role_lib['SPEAKER_00']['wav']
        final_segments = []

        print("\n" + "🛡️"*10 + " 启动特工级自愈流水线 " + "🛡️"*10)

        # 为了演示，我们处理前 20 段 (全篇 114 段耗时过长，建议分批)
        for i, item in enumerate(data[:20]):
            zh_text = item['zh'].strip()
            expected_dur = item['end'] - item['start']
            
            success = False
            for attempt in range(2):
                print(f"  -> [{i+1}/20] 尝试 {attempt}: {zh_text}")
                # 1. 生产 (20-Step极速)
                wav = self.db.model.generate(text=zh_text + "。", reference_wav_path=seed_wav, inference_timesteps=20)
                seg_raw = os.path.join(self.temp_dir, f"raw_{i}.wav")
                sf.write(seg_raw, wav, self.db.sample_rate)
                
                # 2. 审计
                res = self.auditor.transcribe(seg_raw)
                detected = res['text']
                actual_dur = len(wav) / self.db.sample_rate
                
                # 3. 判定
                if actual_dur > expected_dur * 1.3:
                    print(f"     🚩 溢出 ({actual_dur:.1f}s > {expected_dur:.1f}s)。正在自愈...")
                    zh_text = self._get_llm_fix(zh_text, "时长溢出", expected_dur)
                else:
                    success = True
                    break
            
            # 物理截断封装
            final_p = os.path.join(self.temp_dir, f"fixed_{i}.wav")
            # 这里的 atrim 逻辑已由自愈台词保证，仅做最后的安全卡位
            subprocess.run([FFMPEG_BIN, "-y", "-i", seg_raw, "-af", f"atrim=end={expected_dur},asetpts=PTS-STARTPTS,afade=t=out:st={max(0, expected_dur-0.1)}:d=0.1", final_p], capture_output=True)
            final_segments.append((final_p, item['start']))

        # 合并 (Module 3)
        input_args = []
        filter_parts = []
        for idx, (p, start) in enumerate(final_segments):
            input_args.extend(["-i", p])
            filter_parts.append(f"[{idx}:a]adelay={int(start*1000)}|{int(start*1000)}[a{idx}]")
        
        mix_str = "".join([f"[a{k}]" for k in range(len(final_segments))]) + f"amix=inputs={len(final_segments)}:duration=longest"
        subprocess.run([FFMPEG_BIN, "-y"] + input_args + ["-filter_complex", ";".join(filter_parts) + ";" + mix_str, output_wav], check=True)
        print(f"\n🏆 首批特工自愈版已产出：{output_wav}")

if __name__ == "__main__":
    dotenv_p = r"C:\Users\Administrator\Desktop\HorrorAgent_Project\.env"
    with open(dotenv_p, "r") as f:
        key = [l for l in f if "SILICONFLOW_API_KEY" in l][0].split("=")[1].strip().split()[0].replace('"', '').replace("'", "")
    
    factory = AgenticFactory(key)
    factory.process_with_self_healing(
        r"E:\VideoTranslator_Project\unhinged_tech\FINAL_CLEAN_SCRIPT.json",
        r"E:\VideoTranslator_Project\unhinged_tech\UNHINGED_ROLE_LIB.json",
        r"E:\VideoTranslator_Project\output_final\V47_AGENTIC_SAMPLE.wav"
    )

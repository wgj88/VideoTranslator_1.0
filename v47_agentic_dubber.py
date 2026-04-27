# -*- coding: utf-8 -*-
import os, sys, json, subprocess, whisper, numpy as np, librosa
import soundfile as sf

sys.path.append(r"E:\VideoTranslator_Project")
from clone_dubber import VideoCloneDubber

class AgenticDubber:
    def __init__(self, db, auditor, api_key):
        self.db = db
        self.auditor = auditor
        self.api_key = api_key
        self.headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    def _get_llm_fix(self, text, error_type, duration):
        """调用 LLM 导演进行台词自愈"""
        prompt = f"""【台词修复任务】
原始台词：{text}
错误原因：{error_type} (当前时长限额 {duration:.2f}s)
任务：请重新润色台词，确保：
1. 语气更平稳，去除导致音调失控的强烈感叹词。
2. 字数严格适配时间限额。
返回JSON: {{"fixed_zh": "..."}}
"""
        import requests
        payload = {
            "model": "deepseek-ai/DeepSeek-V3",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"}
        }
        r = requests.post("https://api.siliconflow.cn/v1/chat/completions", json=payload, headers=self.headers).json()
        return json.loads(r['choices'][0]['message']['content'])['fixed_zh']

    def dub_with_autofix(self, item, seed_wav, max_retries=2):
        zh_text = item['zh']
        expected_dur = item['end'] - item['start']
        
        for attempt in range(max_retries + 1):
            print(f"     [Attempt {attempt}] 正在尝试: {zh_text}")
            
            # 1. 生成
            wav = self.db.model.generate(text=zh_text + "。", reference_wav_path=seed_wav, inference_timesteps=50)
            
            # 2. 审计
            temp_p = "E:\\VideoTranslator_Project\\temp_factory\\agent_temp.wav"
            sf.write(temp_p, wav, self.db.sample_rate)
            
            # 语义审计
            res = self.auditor.transcribe(temp_p)
            detected_text = res['text']
            
            # 物理偏差审计 (简化逻辑)
            actual_dur = len(wav) / self.db.sample_rate
            
            # --- 判定准则 ---
            error = None
            if len(detected_text) < 2: error = "生成崩溃(胡言乱语)"
            elif actual_dur > expected_dur * 1.5: error = "语速严重过慢/时间轴顶破"
            
            if not error:
                print("     ✅ 审计通过。")
                return wav, zh_text
            
            print(f"     🚩 审计失败: {error}。正在呼叫 LLM 导演进行重编...")
            zh_text = self._get_llm_fix(zh_text, error, expected_dur)

        return wav, zh_text

# 这是一个高度精简的 Agent 演示逻辑

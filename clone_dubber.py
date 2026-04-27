# -*- coding: utf-8 -*-
import os, json, torch, soundfile as sf
from voxcpm import VoxCPM
import traceback, re

class VideoCloneDubber:
    def __init__(self, model_path=r"E:\VideoTranslator_Project\model_weights"):
        print(f"[CloneDubber] 正在以【超稳逻辑模式】加载引擎...")
        # 暂时关闭 load_denoiser 避开 modelscope 依赖，专注参数调优
        self.model = VoxCPM.from_pretrained(model_path, load_denoiser=False)
        self.sample_rate = self.model.tts_model.sample_rate

    def _sanitize_text(self, text):
        text = text.strip()
        if not re.search(r'[。！？]$', text):
            text += "。"
        return text

    def generate_safe(self, text, prompt_wav_path, prompt_text):
        """
        极速冷静推理：Temperature 0.01 绝杀胡言乱语
        """
        print(f"     [Inference] 执行超稳生成 (T=0.01)...")
        return self.model.generate(
            text=text,
            prompt_wav_path=prompt_wav_path,
            prompt_text=prompt_text,
            temperature=0.01,  # 核心：锁定确定性，拒绝幻觉
            top_p=0.8,         # 核心：只保留最高概率音位
            max_new_tokens=1024
        )

if __name__ == "__main__":
    db = VideoCloneDubber()
    print("✅ 引擎重构成功，当前采样率:", db.sample_rate)

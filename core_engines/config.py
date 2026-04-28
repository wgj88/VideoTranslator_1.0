# -*- coding: utf-8 -*-
import os

# --- 核心资产路径 ---
ROOT_DIR = r"E:\VideoTranslator_Project"
FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
FFPROBE_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffprobe.exe"

# --- 模型配置 ---
MODEL_WEIGHTS = os.path.join(ROOT_DIR, "model_weights")
DEFAULT_SEED = os.path.join(ROOT_DIR, "unhinged_tech", "seeds", "ultra_pure_seed.wav")

# --- 生成参数 ---
MAX_TEMPO = 1.4      # 语速加速上限
MIN_CPS = 4.8        # 触发 NLP 精简的每秒字数阈值
VAD_TOP_DB = 22      # 物理断电灵敏度 (越小越灵敏)

# --- 工作空间 ---
WORKSPACE = os.path.join(ROOT_DIR, "production_workspace", "current_run")
OUTPUT_DIR = os.path.join(ROOT_DIR, "output_final")

# 环境变量初始化
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

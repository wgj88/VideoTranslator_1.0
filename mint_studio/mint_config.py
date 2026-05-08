
import os
from pathlib import Path

class MintConfig:
    # --- 基础路径 (自适应) ---
    # 自动定位项目根目录 (E盘挂载点)
    PROJECT_ROOT = Path("/mnt/e/VideoTranslator_Project")
    WORKSPACE = Path("/home/dministrator/video_narration")
    
    # 模型路径
    MODEL_WEIGHTS = PROJECT_ROOT / "model_weights"
    DEFAULT_SEED = PROJECT_ROOT / "unhinged_tech/seeds/ultra_pure_seed_CLEANED.wav"
    SEED_POOL = [
        PROJECT_ROOT / "unhinged_tech/seeds/ultra_pure_seed_CLEANED.wav",
        PROJECT_ROOT / "unhinged_tech/seeds/ultra_pure_seed_SUPER_CLEAN.wav"
    ]
    REINIT_EVERY = 10
    
    # 资产路径
    RAW_VIDEO_DIR = PROJECT_ROOT / "raw_videos"
    SEPARATED_DIR = PROJECT_ROOT / "unhinged_tech/separated_house_wsl/mdx_extra_q"
    OUTPUT_DIR = WORKSPACE / "output/factory_v2"
    
    # --- 生产参数 (解耦) ---
    SAMPLING_RATE = 44100
    LOUDNESS_TARGET = -12.0  # LUFS
    MAX_TEMPO = 1.4
    VAD_TOP_DB = 25
    
    # 侧链参数
    SC_THRESHOLD = 0.1
    SC_RATIO = 4.0
    SC_ATTACK = 20
    SC_RELEASE = 400

    @classmethod
    def ensure_dirs(cls):
        """确保所有必要的生产目录存在"""
        for attr in ["WORKSPACE", "OUTPUT_DIR"]:
            getattr(cls, attr).mkdir(parents=True, exist_ok=True)
        (cls.OUTPUT_DIR / "chunks").mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_bgm_path(cls, video_name):
        """鲁棒的伴奏轨搜寻逻辑"""
        stem = Path(video_name).stem
        ai_path = cls.SEPARATED_DIR / stem / "no_vocals.wav"
        if ai_path.exists():
            return ai_path
        return None

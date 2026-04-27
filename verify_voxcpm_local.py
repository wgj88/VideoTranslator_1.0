import os, torch, soundfile as sf
from voxcpm import VoxCPM

model_path = r'E:\VideoTranslator_Project\model_weights'
output_path = r'E:\VideoTranslator_Project\trans_audio\voxcpm_test.wav'

os.makedirs(os.path.dirname(output_path), exist_ok=True)

try:
    print(f"--- 正在加载 VoxCPM 模型: {model_path} ---")
    model = VoxCPM.from_pretrained(model_path, load_denoiser=False)
    
    test_text = "(A calm male voice) 正在进行本地 VoxCPM 核心测试。这是 48kHz 高保真语音输出。"
    print(f"--- 正在生成语音 ---")
    
    wav = model.generate(text=test_text)
    
    sf.write(output_path, wav, model.tts_model.sample_rate)
    print(f'OK: {output_path}')
except Exception as e:
    print(f'ERROR: {e}')

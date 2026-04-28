# -*- coding: utf-8 -*-
import os, sys, torch

def setup_dll_tunnels():
    """🚀 建立物理级 DLL 搜索隧道，解决 WinError 127"""
    env_base = os.path.dirname(sys.executable)
    paths = [
        os.path.join(env_base, "Lib", "site-packages", "torch", "lib"),
        os.path.join(env_base, "Lib", "site-packages", "torchaudio", "lib"),
        os.path.join(env_base, "Library", "bin")
    ]
    for p in paths:
        if os.path.exists(p):
            os.add_dll_directory(p)
            print(f"✅ 隧道已贯通: {p}")

if __name__ == "__main__":
    setup_dll_tunnels()
    
    try:
        import torchaudio
        from voxcpm import VoxCPM
        import soundfile as sf
        
        print(f"🔥 全链路激活成功！\nTorch: {torch.__version__}\nAudio: {torchaudio.__version__}\nCUDA: {torch.cuda.is_available()}")
        
        # 终极渲染测试
        print("\n--- 正在进行 5060 Ti 巅峰性能首秀 ---")
        model = VoxCPM.from_pretrained(r"E:\VideoTranslator_Project\model_weights")
        wav = model.generate(text="(A deep voice) 恭喜！Blackwell 架构已全面解锁。视频汉化工厂正式投产。")
        os.makedirs("trans_audio", exist_ok=True)
        sf.write("trans_audio/victory_final.wav", wav, model.tts_model.sample_rate)
        print("🎉 震撼！本地极速渲染完成：trans_audio/victory_final.wav")
        
    except Exception as e:
        print(f"❌ 最终战役受阻: {e}")

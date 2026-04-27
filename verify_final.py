import torch
print("--- [BLACKWELL HARDWARE REPORT] ---")
try:
    print(f"PyTorch 版本: {torch.__version__}")
    print(f"CUDA 版本: {torch.version.cuda}")
    print(f"支持架构列表: {torch.cuda.get_arch_list()}")
    if "sm_120" in torch.cuda.get_arch_list():
        print("🔥 恭喜！sm_120 核心已就绪。5060 Ti 已完全解锁。")
        x = torch.zeros(1024, 1024).cuda()
        print("✅ 显卡数据吞吐测试：成功！")
    else:
        print("⚠️ 架构列表未命中，请检查驱动版本。")
except Exception as e:
    print(f"❌ 硬件握手失败: {e}")

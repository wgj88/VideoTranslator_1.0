import torch
print("--- [Blackwell Hardware Verification] ---")
try:
    print(f"PyTorch 版本: {torch.__version__}")
    print(f"CUDA 版本: {torch.version.cuda}")
    print(f"显卡名称: {torch.cuda.get_device_name(0)}")
    print(f"支持架构列表: {torch.cuda.get_arch_list()}")
    
    if "sm_120" in torch.cuda.get_arch_list():
        print("🔥 恭喜！sm_120 (Blackwell) 架构已成功加载。")
        x = torch.zeros(1024, 1024).cuda()
        print("✅ 显卡数据吞吐测试：成功！")
    else:
        print("⚠️ 虽然 CUDA 激活，但 sm_120 仍不在支持列表中。")
except Exception as e:
    print(f"❌ 硬件连接崩溃: {e}")

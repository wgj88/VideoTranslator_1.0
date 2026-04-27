import torch
print("--- [GPU Deep Check] ---")
try:
    available = torch.cuda.is_available()
    print(f"CUDA 可用性: {available}")
    if available:
        device_count = torch.cuda.device_count()
        name = torch.cuda.get_device_name(0)
        capability = torch.cuda.get_device_capability(0)
        print(f"发现显卡: {name}")
        print(f"算力等级 (Capability): {capability}")
        # 尝试创建一个张量，测试内核是否真的能运行
        x = torch.ones(1).cuda()
        print("✅ 内核测试成功：显卡已成功处理数据！")
    else:
        print("❌ 依然没有检测到 CUDA 设备")
except Exception as e:
    print(f"❌ 运行测试时崩溃: {e}")

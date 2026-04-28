# -*- coding: utf-8 -*-
import os, shutil

def deep_cleanup():
    root = r"E:\VideoTranslator_Project"
    archive_dir = os.path.join(root, "archive", "iterations")
    engine_dir = os.path.join(root, "core_engines")
    pkg_dir = os.path.join(root, "archive", "install_packages")
    
    os.makedirs(archive_dir, exist_ok=True)
    os.makedirs(engine_dir, exist_ok=True)
    os.makedirs(pkg_dir, exist_ok=True)

    files = os.listdir(root)
    print(f"🧹 正在清理 {len(files)} 个项...")

    # 1. 移动核心引擎
    core_files = ["clone_dubber.py", "factory_final_v1_0.py"]
    for f in core_files:
        src = os.path.join(root, f)
        if os.path.exists(src):
            shutil.move(src, os.path.join(engine_dir, f))
            print(f"  📦 固化引擎: {f}")

    # 2. 处理 V92 旗舰版：更名为生产启动器
    v92_src = os.path.join(root, "v92_master_run.py")
    if os.path.exists(v92_src):
        shutil.copy(v92_src, os.path.join(root, "start_production.py"))
        print("  🚀 已生成全局启动器: start_production.py")

    # 3. 归档所有旧脚本 (v*.py, audit_*, run_*, build_*, etc.)
    for f in files:
        if not f.endswith(".py"): continue
        if f in ["start_production.py", "clone_dubber.py", "factory_final_v1_0.py"]: continue
        
        src = os.path.join(root, f)
        shutil.move(src, os.path.join(archive_dir, f))

    # 4. 处理巨大的 .whl 包
    for f in files:
        if f.endswith(".whl"):
            shutil.move(os.path.join(root, f), os.path.join(pkg_dir, f))
            print(f"  💾 归档重型依赖包: {f}")

    print("\n✅ 项目空间已净化！目前根目录仅保留生产级入口。")

if __name__ == "__main__":
    deep_cleanup()

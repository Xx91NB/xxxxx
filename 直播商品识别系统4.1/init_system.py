#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统初始化脚本
"""
import sys
import os
from pathlib import Path

def init_system():
    """初始化系统"""
    print("初始化系统...")
    
    # 检查Python依赖
    try:
        import cv2
        print(f"✓ OpenCV版本: {cv2.__version__}")
    except ImportError:
        print("✗ OpenCV未安装，请运行: pip install opencv-python opencv-contrib-python")
        return False
    
    # 检查其他依赖
    try:
        import yaml, numpy, PIL, mss, pyautogui
        print("✓ 所有依赖已安装")
    except ImportError as e:
        print(f"✗ 缺少依赖: {e}")
        return False
    
    # 创建目录
    dirs = ["data", "data/images_material", "data/learned_samples", 
            "outputs", "config", "logs"]
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    print("✓ 目录创建完成")
    
    # 检查项目文件
    required_files = ["output_manager.py", "smart_main.py", "screen_recognition.py"]
    for file in required_files:
        if not Path(file).exists():
            print(f"✗ 未找到文件: {file}")
            return False
    print("✓ 项目文件检查完成")
    
    # 初始化输出管理器
    try:
        sys.path.append('.')
        from output_manager import get_output_manager
        mgr = get_output_manager()
        print("✓ 输出管理器初始化成功")
        print("输出文件:")
        for name, path in mgr.output_files.items():
            print(f"  - {name}: {path}")
    except Exception as e:
        print(f"✗ 输出管理器初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    if init_system():
        sys.exit(0)
    else:
        sys.exit(1)
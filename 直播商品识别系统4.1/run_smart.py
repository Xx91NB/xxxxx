#!/usr/bin/env python3
"""
智能系统简化启动脚本
"""
import sys
import os

def main():
    print("直播商品识别系统 - 智能版")
    print("=" * 50)
    
    # 检查依赖
    try:
        import cv2
        import numpy as np
        import yaml
        from PIL import Image
        print("✓ 所有依赖已安装")
    except ImportError as e:
        print(f"✗ 缺少依赖: {e}")
        print("正在安装依赖...")
        
        try:
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", 
                                 "opencv-python", "opencv-contrib-python", 
                                 "numpy", "pyyaml", "pillow"])
            print("✓ 依赖安装完成")
        except:
            print("依赖安装失败，请手动运行:")
            print("pip install opencv-python opencv-contrib-python numpy pyyaml pillow")
            input("按Enter键退出...")
            return
    
    # 创建必要目录
    os.makedirs("data/images_material", exist_ok=True)
    os.makedirs("data/learned_samples", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)
    os.makedirs("utils", exist_ok=True)
    
    # 导入主程序
    try:
        from smart_main import main as smart_main
        smart_main()
    except ImportError as e:
        print(f"导入主程序失败: {e}")
        print("请确保所有文件都在正确的位置")
        input("按Enter键退出...")

if __name__ == "__main__":
    main()
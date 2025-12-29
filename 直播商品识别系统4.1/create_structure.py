#!/usr/bin/env python3
"""
项目结构生成器
运行此脚本创建完整的项目结构
"""
import os
from pathlib import Path

def create_project_structure():
    """创建项目目录结构"""
    print("创建直播商品识别系统项目结构...")
    
    # 项目根目录
    root_dir = Path(".")
    
    # 定义目录结构
    dir_structure = [
        # 数据目录
        "data/images",
        "data/videos",
        "data/images_material",
        "data/videos_material",
        "data/learned_samples",
        "data/raw_videos",
        
        # 输出目录
        "outputs/logs",
        "outputs/reports",
        "outputs/screenshots",
        "outputs/unknown",
        "outputs/video_matches",
        
        # 配置目录
        "config",
        
        # 核心代码目录
        "core",
        
        # 工具目录
        "tools",
        
        # 文档目录
        "docs",
        
        # 模型目录
        "models"
    ]
    
    # 创建目录
    created_count = 0
    for dir_path in dir_structure:
        path = Path(dir_path)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print(f"✓ 创建目录: {dir_path}")
            created_count += 1
        else:
            print(f"  ✓ 目录已存在: {dir_path}")
    
    print(f"\n共创建/确认 {created_count} 个目录")
    
    # 创建示例文件
    create_example_files()
    
    print("\n项目结构创建完成！")

def create_example_files():
    """创建示例文件"""
    print("\n创建示例文件...")
    
    # 在images_material中创建示例商品图片
    create_sample_products()
    
    # 创建默认配置文件
    create_default_config()
    
    # 创建README说明
    create_readme_file()
    
    print("示例文件创建完成")

def create_sample_products():
    """创建示例商品图片"""
    try:
        import cv2
        import numpy as np
        
        template_dir = Path("data/images_material")
        
        # 示例商品定义
        sample_products = [
            {
                "name": "手机",
                "color": (100, 50, 50),  # 蓝色
                "shape": "rectangle",
                "size": (150, 200)
            },
            {
                "name": "水杯", 
                "color": (50, 100, 50),  # 绿色
                "shape": "cylinder",
                "size": (120, 180)
            },
            {
                "name": "书本",
                "color": (50, 50, 100),  # 红色
                "size": (140, 190)
            }
        ]
        
        created_count = 0
        for product in sample_products:
            name = product["name"]
            color = product["color"]
            
            # 创建图像
            img = np.zeros((250, 250, 3), dtype=np.uint8)
            img[:] = (240, 240, 240)  # 浅灰色背景
            
            # 绘制商品形状
            center_x, center_y = 125, 125
            width, height = 150, 200
            
            # 绘制矩形商品
            cv2.rectangle(img, 
                         (center_x - width//2, center_y - height//2),
                         (center_x + width//2, center_y + height//2),
                         color, -1)
            
            # 添加商品名称
            cv2.putText(img, name, 
                       (center_x - 40, center_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
            # 保存图像
            filename = template_dir / f"{name}.jpg"
            cv2.imwrite(str(filename), img)
            created_count += 1
            
            print(f"  创建示例商品: {name}")
        
        print(f"✓ 创建了 {created_count} 个示例商品图片")
        
    except ImportError:
        print("  ⚠ 无法创建示例图片 (需要OpenCV)")
    except Exception as e:
        print(f"  ⚠ 创建示例图片失败: {e}")

def create_default_config():
    """创建默认配置文件"""
    try:
        import yaml
        
        config_dir = Path("config")
        
        # 创建默认配置文件
        default_config = {
            'project': {
                'name': '直播商品识别系统',
                'version': '4.1',
                'description': '基于计算机视觉的商品识别系统'
            },
            'system': {
                'default_mode': 'hybrid',
                'auto_save': True,
                'auto_save_interval': 300
            },
            'paths': {
                'data': './data',
                'outputs': './outputs',
                'config': './config'
            },
            'detection': {
                'confidence_threshold': 0.5
            },
            'matching': {
                'min_matches': 10
            }
        }
        
        config_file = config_dir / "default.yaml"
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True)
        
        print("✓ 创建默认配置文件: config/default.yaml")
        
    except ImportError:
        print("  ⚠ 无法创建配置文件 (需要PyYAML)")
    except Exception as e:
        print(f"  ⚠ 创建配置文件失败: {e}")

def create_readme_file():
    """创建README文件"""
    readme_content = """# 直播商品识别系统 4.1

## 项目简介
基于计算机视觉的智能商品识别系统，支持实时视频流和图像的商品检测与识别。

## 快速开始

### 1. 安装依赖
```bash
pip install opencv-python opencv-contrib-python numpy pyyaml pillow
#!/usr/bin/env python3
"""
素材检查工具
检查项目所需的素材文件是否齐全
"""
import os
from pathlib import Path

def check_materials():
    """检查素材文件"""
    print("=" * 50)
    print("      素材完整性检查")
    print("=" * 50)
    
    # 定义需要检查的目录
    required_dirs = [
        "data/images",
        "data/videos", 
        "data/images_material",
        "data/videos_material",
        "outputs",
        "config"
    ]
    
    print("\n检查目录结构...")
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"✓ {dir_path}")
        else:
            print(f"✗ {dir_path} (不存在)")
            path.mkdir(parents=True, exist_ok=True)
            print(f"  已自动创建")
    
    # 检查配置文件
    print("\n检查配置文件...")
    config_files = [
        "config/default.yaml",
        "config/calibration.yaml"
    ]
    
    for config_file in config_files:
        path = Path(config_file)
        if path.exists():
            print(f"✓ {config_file}")
        else:
            print(f"✗ {config_file} (不存在)")
    
    # 创建默认配置文件（如果不存在）
    create_default_config()
    
    # 检查样本素材
    print("\n检查样本素材...")
    check_sample_materials()
    
    print("\n" + "=" * 50)
    print("检查完成！")
    
    # 显示统计信息
    show_statistics()

def create_default_config():
    """创建默认配置文件"""
    config_path = Path("config/default.yaml")
    
    if not config_path.exists():
        print("创建默认配置文件...")
        
        config = {
            'project': {
                'name': '直播商品识别系统',
                'version': '4.0',
                'author': '用户'
            },
            'paths': {
                'data': './data',
                'outputs': './outputs',
                'config': './config'
            },
            'detection': {
                'confidence_threshold': 0.5,
                'min_object_size': 50
            },
            'matching': {
                'method': 'orb',
                'min_matches': 10
            }
        }
        
        import yaml
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        
        print(f"默认配置已创建: {config_path}")

def check_sample_materials():
    """检查样本素材"""
    # 创建一些示例文件（如果目录为空）
    image_dir = Path("data/images_material")
    video_dir = Path("data/videos_material")
    
    # 检查图像素材
    image_files = list(image_dir.glob("*.*"))
    if len(image_files) == 0:
        print("⚠ 图像素材目录为空")
        print("  提示: 请在 data/images_material 中添加商品图片")
    else:
        print(f"✓ 找到 {len(image_files)} 个图像素材")
    
    # 检查视频素材
    video_files = list(video_dir.glob("*.*"))
    if len(video_files) == 0:
        print("⚠ 视频素材目录为空")
        print("  提示: 请在 data/videos_material 中添加商品视频")
    else:
        print(f"✓ 找到 {len(video_files)} 个视频素材")

def show_statistics():
    """显示统计信息"""
    print("\n=== 统计信息 ===")
    
    directories = [
        ("图像素材", Path("data/images_material")),
        ("视频素材", Path("data/videos_material")),
        ("输入图像", Path("data/images")),
        ("输入视频", Path("data/videos")),
        ("输出文件", Path("outputs"))
    ]
    
    for name, path in directories:
        if path.exists():
            # 计算文件数量
            files = list(path.rglob("*.*"))
            file_count = len([f for f in files if f.is_file()])
            
            # 计算总大小
            total_size = sum(f.stat().st_size for f in files if f.is_file())
            size_mb = total_size / (1024 * 1024)
            
            print(f"{name}: {file_count} 个文件, {size_mb:.1f} MB")
        else:
            print(f"{name}: 目录不存在")

if __name__ == "__main__":
    check_materials()
    input("\n按任意键退出...")
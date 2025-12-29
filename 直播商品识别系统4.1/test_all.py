#!/usr/bin/env python3
"""
系统测试脚本
测试所有模块是否正常工作
"""
import sys
import os
import cv2
import numpy as np
from pathlib import Path

def print_header(title):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_opencv():
    """测试OpenCV"""
    print_header("测试OpenCV")
    
    try:
        print(f"OpenCV版本: {cv2.__version__}")
        
        # 测试读取图像
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        cv2.rectangle(test_image, (20, 20), (80, 80), (0, 255, 0), 2)
        
        # 测试显示图像
        cv2.imshow('OpenCV测试', test_image)
        cv2.waitKey(100)
        cv2.destroyAllWindows()
        
        print("✓ OpenCV测试通过")
        return True
        
    except Exception as e:
        print(f"✗ OpenCV测试失败: {e}")
        return False

def test_directories():
    """测试目录结构"""
    print_header("测试目录结构")
    
    required_dirs = [
        "data",
        "data/images",
        "data/videos", 
        "data/images_material",
        "data/videos_material",
        "outputs",
        "config",
        "core"
    ]
    
    all_ok = True
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"✓ {dir_path}")
        else:
            print(f"✗ {dir_path} (不存在，正在创建...)")
            try:
                path.mkdir(parents=True, exist_ok=True)
                print(f"  → 已创建")
            except Exception as e:
                print(f"  → 创建失败: {e}")
                all_ok = False
    
    return all_ok

def test_config_files():
    """测试配置文件"""
    print_header("测试配置文件")
    
    config_files = [
        "config/default.yaml",
        "config/hybrid_mode.yaml",
        "config/image_mode.yaml",
        "config/video_mode.yaml"
    ]
    
    all_ok = True
    for config_file in config_files:
        path = Path(config_file)
        if path.exists():
            print(f"✓ {config_file}")
            
            # 尝试读取配置文件
            try:
                import yaml
                with open(path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                print(f"  配置文件格式正确")
            except Exception as e:
                print(f"  配置文件读取错误: {e}")
                all_ok = False
        else:
            print(f"⚠ {config_file} (不存在)")
            all_ok = False
    
    return all_ok

def test_detector_module():
    """测试检测器模块"""
    print_header("测试检测器模块")
    
    try:
        from detector import ProductDetector
        
        # 创建检测器
        detector = ProductDetector()
        print("✓ 检测器导入成功")
        
        # 测试检测功能
        test_image = np.zeros((300, 300, 3), dtype=np.uint8)
        detections = detector.detect(test_image)
        
        print(f"✓ 检测功能正常 (检测到 {len(detections)} 个对象)")
        return True
        
    except ImportError as e:
        print(f"✗ 无法导入检测器: {e}")
        return False
    except Exception as e:
        print(f"✗ 检测器测试失败: {e}")
        return False

def test_image_matcher_module():
    """测试图像匹配器模块"""
    print_header("测试图像匹配器模块")
    
    try:
        from image_matcher import ImageMatcher
        
        # 创建匹配器
        matcher = ImageMatcher()
        print("✓ 图像匹配器导入成功")
        
        # 创建测试图像
        img1 = np.zeros((200, 200, 3), dtype=np.uint8)
        cv2.rectangle(img1, (50, 50), (150, 150), (255, 0, 0), -1)
        
        img2 = np.zeros((200, 200, 3), dtype=np.uint8)
        cv2.rectangle(img2, (60, 60), (160, 160), (255, 0, 0), -1)
        
        # 测试特征提取
        kp1, desc1 = matcher.extract_features(img1)
        print(f"✓ 特征提取正常 (关键点数: {len(kp1) if kp1 else 0})")
        
        # 测试添加模板
        matcher.add_template("test_template", img1)
        print("✓ 模板添加正常")
        
        return True
        
    except ImportError as e:
        print(f"✗ 无法导入图像匹配器: {e}")
        return False
    except Exception as e:
        print(f"✗ 图像匹配器测试失败: {e}")
        return False

def test_camera():
    """测试摄像头"""
    print_header("测试摄像头")
    
    try:
        # 尝试多个摄像头索引
        for camera_id in [0, 1, 2]:
            cap = cv2.VideoCapture(camera_id)
            
            if cap.isOpened():
                print(f"尝试摄像头 {camera_id}...")
                # 读取一帧测试
                ret, frame = cap.read()
                cap.release()
                
                if ret and frame is not None:
                    print(f"✓ 摄像头 {camera_id} 正常 (图像尺寸: {frame.shape[1]}x{frame.shape[0]})")
                    return True
                else:
                    print(f"摄像头 {camera_id} 无法读取图像")
            else:
                print(f"摄像头 {camera_id} 无法打开")
        
        print("✗ 无法打开任何摄像头 (可能未连接或无权限)")
        return False
            
    except Exception as e:
        print(f"✗ 摄像头测试失败: {e}")
        return False
def test_import_all_modules():
    """测试导入所有模块"""
    print_header("测试导入所有模块")
    
    modules_to_test = [
        ("detector", "ProductDetector"),
        ("image_matcher", "ImageMatcher"),
        ("video_matcher", "VideoMatcher"),
        ("advanced_matcher", "AdvancedMatcher"),
        ("calibrate_region", "Calibrator"),
        ("check_materials", None),
        ("core.intelligent_system", "IntelligentSystem")
    ]
    
    all_ok = True
    for module_name, class_name in modules_to_test:
        try:
            if class_name:
                exec(f"from {module_name} import {class_name}")
                print(f"✓ {module_name}.{class_name}")
            else:
                exec(f"import {module_name}")
                print(f"✓ {module_name}")
        except ImportError as e:
            print(f"✗ 无法导入 {module_name}: {e}")
            all_ok = False
        except Exception as e:
            print(f"✗ {module_name} 导入错误: {e}")
            all_ok = False
    
    return all_ok

def create_sample_data():
    """创建示例数据"""
    print_header("创建示例数据")
    
    # 创建示例商品图片
    sample_dir = Path("data/images_material")
    sample_dir.mkdir(exist_ok=True)
    
    # 创建几个示例商品图片
    products = [
        ("product_red", (255, 0, 0)),    # 红色商品
        ("product_green", (0, 255, 0)),  # 绿色商品  
        ("product_blue", (0, 0, 255)),   # 蓝色商品
    ]
    
    created_count = 0
    for name, color in products:
        # 创建测试图像
        img = np.zeros((200, 200, 3), dtype=np.uint8)
        cv2.rectangle(img, (50, 50), (150, 150), color, -1)
        
        # 添加文本
        cv2.putText(img, name, (60, 120), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # 保存
        filename = sample_dir / f"{name}.jpg"
        cv2.imwrite(str(filename), img)
        created_count += 1
    
    print(f"✓ 创建了 {created_count} 个示例商品图片")
    
    # 创建配置示例
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    # 创建默认配置（如果不存在）
    default_config = Path("config/default.yaml")
    if not default_config.exists():
        import yaml
        
        config_data = {
            'project': {
                'name': '直播商品识别系统',
                'version': '4.1'
            },
            'system': {
                'default_mode': 'hybrid'
            }
        }
        
        with open(default_config, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
        
        print("✓ 创建了默认配置文件")
    
    return True

def run_comprehensive_test():
    """运行全面测试"""
    print("\n" + "=" * 60)
    print("        直播商品识别系统 - 全面测试")
    print("=" * 60)
    
    test_results = []
    
    # 运行各个测试
    test_results.append(("OpenCV", test_opencv()))
    test_results.append(("目录结构", test_directories()))
    test_results.append(("配置文件", test_config_files()))
    test_results.append(("检测器模块", test_detector_module()))
    test_results.append(("图像匹配器", test_image_matcher_module()))
    test_results.append(("摄像头", test_camera()))
    test_results.append(("所有模块导入", test_import_all_modules()))
    test_results.append(("示例数据", create_sample_data()))
    
    # 打印总结
    print_header("测试总结")
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    print(f"测试通过: {passed}/{total}")
    
    for test_name, result in test_results:
        status = "✓" if result else "✗"
        print(f"  {status} {test_name}")
    
    if passed == total:
        print("\n🎉 所有测试通过！系统可以正常运行。")
        print("建议下一步:")
        print("  1. 运行 'python start.py' 启动系统")
        print("  2. 放入真实的商品图片到 data/images_material/")
        print("  3. 运行 'python main.py' 开始商品识别")
    else:
        print(f"\n⚠  {total - passed} 个测试失败。")
        print("请检查以上错误信息并修复。")
    
    return passed == total

def main():
    """主函数"""
    try:
        success = run_comprehensive_test()
        
        if success:
            # 询问是否运行演示
            print("\n" + "-" * 60)
            choice = input("是否运行快速演示？ (y/n): ").strip().lower()
            
            if choice == 'y':
                run_quick_demo()
        else:
            print("\n⚠ 系统测试未通过，请先解决上述问题。")
            
    except KeyboardInterrupt:
        print("\n\n测试被用户中断。")
    except Exception as e:
        print(f"\n❌ 测试过程中发生未知错误: {e}")
        import traceback
        traceback.print_exc()
    
    input("\n按Enter键退出...")

def run_quick_demo():
    """运行快速演示"""
    print_header("快速演示")
    
    try:
        print("1. 测试图像匹配...")
        import cv2  # 添加这行
        from image_matcher import ImageMatcher
        
        # 创建匹配器
        matcher = ImageMatcher()
        
        # 加载示例模板
        sample_dir = Path("data/images_material")
        if sample_dir.exists():
            count = matcher.load_templates_from_dir(sample_dir)
            print(f"  加载了 {count} 个模板")
        
        # 创建测试图像
        test_img = np.zeros((300, 300, 3), dtype=np.uint8)
        cv2.rectangle(test_img, (100, 100), (200, 200), (0, 255, 0), -1)
        
        # 进行匹配
        matches = matcher.match(test_img)
        print(f"  找到 {len(matches)} 个匹配")
        
        print("2. 测试摄像头实时检测...")
        print("   按 'q' 退出演示窗口")
        
        # 尝试多个摄像头
        for camera_id in [0, 1, 2]:
            cap = cv2.VideoCapture(camera_id)
            if cap.isOpened():
                print(f"   打开摄像头 {camera_id}")
                break
            else:
                cap.release()
        else:
            print("   无法打开摄像头，跳过此演示")
            return
        
        # 运行几秒钟的演示
        import time
        end_time = time.time() + 5  # 运行5秒
        
        while time.time() < end_time:
            ret, frame = cap.read()
            if not ret:
                break
            
            # 在图像中心画一个示例框
            h, w = frame.shape[:2]
            cv2.rectangle(frame, 
                         (w//4, h//4), 
                         (3*w//4, 3*h//4), 
                         (0, 255, 0), 2)
            
            cv2.putText(frame, "Demo - Product Detection", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.7, (0, 255, 0), 2)
            
            cv2.imshow("Quick Demo - Press 'q' to exit", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        print("✅ 演示完成！")
        
    except Exception as e:
        print(f"演示失败: {e}")

if __name__ == "__main__":
    main()
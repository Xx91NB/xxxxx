#!/usr/bin/env python3
"""
快速启动脚本
最简单的启动方式
"""
import os
import sys
from pathlib import Path

def main():
    print("直播商品识别系统 4.1 - 快速启动")
    print("=" * 50)
    
    # 检查依赖
    print("检查依赖...")
    try:
        import cv2
        import numpy as np
        import yaml
        print("✓ 所有依赖已安装")
    except ImportError as e:
        print(f"✗ 缺少依赖: {e}")
        print("请运行: pip install opencv-python numpy pyyaml")
        input("按Enter键退出...")
        return
    
    # 检查目录
    print("检查目录结构...")
    directories = ["data/images_material", "outputs", "config"]
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✓ {dir_path}")
    
    # 创建默认配置（如果不存在）
    config_file = Path("config/default.yaml")
    if not config_file.exists():
        print("创建默认配置...")
        import yaml
        
        config = {
            'project': {
                'name': '直播商品识别系统',
                'version': '4.1'
            },
            'system': {
                'default_mode': 'hybrid',
                'auto_save': True
            }
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        
        print(f"✓ 配置文件已创建: {config_file}")
    
    # 显示菜单
    print("\n请选择启动方式:")
    print("1. 主程序菜单 (推荐)")
    print("2. 摄像头实时检测")
    print("3. 图像匹配测试")
    print("4. 系统测试")
    print("5. 退出")
    
    choice = input("\n请输入选项 (1-5): ").strip()
    
    if choice == "1":
        start_main_program()
    elif choice == "2":
        start_camera_demo()
    elif choice == "3":
        start_image_matching_test()
    elif choice == "4":
        run_system_test()
    elif choice == "5":
        print("再见！")
        return
    else:
        print("无效选项")

def start_main_program():
    """启动主程序"""
    print("\n启动主程序...")
    
    try:
        # 导入main模块
        import main
        # 检查是否有main函数
        if hasattr(main, 'main_menu'):
            main.main_menu()
        elif hasattr(main, 'main'):
            main.main()
        else:
            print("找不到主函数，启动简单界面")
            start_simple_gui()
    except ImportError as e:
        print(f"导入main模块失败: {e}")
        start_simple_gui()

def start_simple_gui():
    """启动简单的GUI"""
    try:
        import cv2
        import numpy as np
        
        print("启动简单摄像头界面...")
        print("按 'q' 退出，按 's' 保存截图")
        
        # 尝试多个摄像头
        for camera_id in [0, 1, 2]:
            cap = cv2.VideoCapture(camera_id)
            if cap.isOpened():
                print(f"✓ 打开摄像头 {camera_id}")
                break
            else:
                cap.release()
        else:
            print("无法打开任何摄像头！")
            return
        
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # 添加简单界面元素
            h, w = frame.shape[:2]
            
            # 绘制检测区域
            cv2.rectangle(frame, (w//4, h//4), (3*w//4, 3*h//4), (0, 255, 0), 2)
            
            # 添加文字
            cv2.putText(frame, "Live Product Recognition", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Frame: {frame_count}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(frame, "Press 'q' to quit, 's' to save", (10, 90),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            cv2.imshow("Product Recognition - Simple GUI", frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                # 保存截图
                import time
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"outputs/screenshot_{timestamp}.jpg"
                cv2.imwrite(filename, frame)
                print(f"截图已保存: {filename}")
        
        cap.release()
        cv2.destroyAllWindows()
        print(f"共处理 {frame_count} 帧")
        
    except Exception as e:
        print(f"GUI启动失败: {e}")

def start_camera_demo():
    """启动摄像头演示"""
    print("\n启动摄像头演示...")
    
    try:
        import cv2
        import time
        
        # 尝试多个摄像头
        for camera_id in [0, 1, 2]:
            cap = cv2.VideoCapture(camera_id)
            if cap.isOpened():
                print(f"✓ 打开摄像头 {camera_id}")
                break
            else:
                cap.release()
        else:
            print("无法打开任何摄像头")
            return
        
        print("摄像头已打开")
        print("按 'q' 退出，按 's' 保存截图")
        
        frame_count = 0
        start_time = time.time()
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # 计算FPS
            elapsed = time.time() - start_time
            fps = frame_count / elapsed if elapsed > 0 else 0
            
            # 在图像上添加信息
            h, w = frame.shape[:2]
            
            # 绘制中心区域（模拟检测区域）
            center_x, center_y = w // 2, h // 2
            size = min(w, h) // 3
            
            cv2.rectangle(frame, 
                         (center_x - size//2, center_y - size//2),
                         (center_x + size//2, center_y + size//2),
                         (0, 255, 0), 2)
            
            # 添加文字信息
            info_lines = [
                "Camera Demo - Product Recognition",
                f"Resolution: {w}x{h}",
                f"FPS: {fps:.1f}",
                "Press 'q' to quit, 's' to save"
            ]
            
            y_offset = 30
            for line in info_lines:
                cv2.putText(frame, line, (10, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                y_offset += 25
            
            cv2.imshow("Camera Demo", frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"outputs/demo_screenshot_{timestamp}.jpg"
                cv2.imwrite(filename, frame)
                print(f"截图已保存: {filename}")
        
        cap.release()
        cv2.destroyAllWindows()
        
        print(f"演示结束，共处理 {frame_count} 帧")
        
    except Exception as e:
        print(f"摄像头演示失败: {e}")

def start_image_matching_test():
    """启动图像匹配测试"""
    print("\n启动图像匹配测试...")
    
    try:
        from image_matcher import ImageMatcher
        import cv2
        import numpy as np
        
        # 创建匹配器
        matcher = ImageMatcher()
        
        # 检查是否有模板
        template_dir = Path("data/images_material")
        if not template_dir.exists() or len(list(template_dir.glob("*.*"))) == 0:
            print("没有找到模板图片，请先放入商品图片到 data/images_material/")
            print("正在创建示例模板...")
            create_sample_templates()
        
        # 加载模板
        count = matcher.load_templates_from_dir(template_dir)
        print(f"加载了 {count} 个模板")
        
        # 创建测试图像
        print("创建测试图像...")
        test_img = create_test_image()
        
        # 进行匹配
        print("进行图像匹配...")
        matches = matcher.match(test_img)
        
        if matches:
            best_match = matches[0]
            print(f"最佳匹配: {best_match['template_name']}")
            print(f"匹配点数: {best_match['match_count']}")
            print(f"匹配质量: {best_match['quality']:.2f}")
            
            # 显示匹配结果
            result_img = matcher.draw_matches(test_img, best_match)
            cv2.imshow("Image Matching Result", result_img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        else:
            print("没有找到匹配")
        
        print("图像匹配测试完成")
        
    except Exception as e:
        print(f"图像匹配测试失败: {e}")

def create_sample_templates():
    """创建示例模板"""
    import cv2
    import numpy as np
    
    template_dir = Path("data/images_material")
    template_dir.mkdir(exist_ok=True)
    
    # 创建几个示例模板
    templates = [
        ("手机", (100, 50, 50)),
        ("水杯", (50, 100, 50)),
        ("书本", (50, 50, 100))
    ]
    
    for name, color in templates:
        img = np.zeros((200, 200, 3), dtype=np.uint8)
        cv2.rectangle(img, (30, 30), (170, 170), color, -1)
        cv2.putText(img, name, (60, 110), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        filename = template_dir / f"{name}.jpg"
        cv2.imwrite(str(filename), img)
        print(f"创建模板: {name}")
    
    print(f"在 {template_dir} 中创建了 {len(templates)} 个示例模板")

def create_test_image():
    """创建测试图像"""
    import cv2
    import numpy as np
    
    # 创建一个与模板相似的测试图像
    img = np.zeros((300, 400, 3), dtype=np.uint8)
    
    # 模拟一个商品
    cv2.rectangle(img, (100, 80), (200, 180), (100, 50, 50), -1)
    cv2.putText(img, "测试商品", (110, 140), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    return img

def run_system_test():
    """运行系统测试"""
    print("\n运行系统测试...")
    
    try:
        import test_all
        test_all.run_comprehensive_test()
    except ImportError:
        print("测试脚本不存在")
    except Exception as e:
        print(f"系统测试失败: {e}")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
直播商品识别系统 - 最简单启动脚本
双击此文件即可运行
"""
import os
import sys
from pathlib import Path

def main():
    print("直播商品识别系统 4.1")
    print("=" * 50)
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("错误: 需要Python 3.8或更高版本")
        input("按Enter键退出...")
        return
    
    # 检查依赖
    try:
        import cv2
        import numpy as np
        print("✓ 依赖检查通过")
    except ImportError as e:
        print(f"✗ 缺少依赖: {e}")
        print("正在安装依赖...")
        
        try:
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", 
                                 "opencv-python", "numpy", "pyyaml", "pillow"])
            print("✓ 依赖安装完成")
        except:
            print("依赖安装失败，请手动运行:")
            print("pip install opencv-python numpy pyyaml pillow")
            input("按Enter键退出...")
            return
    
    # 创建必要目录
    Path("data/images_material").mkdir(parents=True, exist_ok=True)
    Path("outputs").mkdir(exist_ok=True)
    Path("config").mkdir(exist_ok=True)
    
    # 显示菜单
    print("\n请选择启动方式:")
    print("1. 主程序 (完整功能)")
    print("2. 摄像头实时检测")
    print("3. 图像匹配测试")
    print("4. 系统测试")
    print("5. 退出")
    
    choice = input("\n请选择 (1-5): ").strip()
    
    if choice == "1":
        import main
        main.main_menu()
    elif choice == "2":
        run_camera_demo()
    elif choice == "3":
        run_image_match_test()
    elif choice == "4":
        import test_all
        test_all.run_comprehensive_test()
    elif choice == "5":
        print("再见！")
    else:
        print("无效选择")

def run_camera_demo():
    """运行摄像头演示"""
    import cv2
    import time
    
    print("\n启动摄像头演示...")
    print("按 'q' 退出")
    
    # 尝试多个摄像头
    for camera_id in [0, 1, 2]:
        cap = cv2.VideoCapture(camera_id)
        if cap.isOpened():
            print(f"打开摄像头 {camera_id}")
            break
        cap.release()
    else:
        print("无法打开摄像头")
        return
    
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
        
        # 添加信息
        h, w = frame.shape[:2]
        cv2.putText(frame, "摄像头演示", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"FPS: {fps:.1f}", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(frame, "按 'q' 退出", (10, 90),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        cv2.imshow("摄像头演示", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print(f"演示结束，共处理 {frame_count} 帧")

def run_image_match_test():
    """运行图像匹配测试"""
    try:
        from image_matcher import ImageMatcher
        import cv2
        import numpy as np
        
        print("\n图像匹配测试...")
        
        # 创建匹配器
        matcher = ImageMatcher()
        
        # 创建测试模板
        template_dir = Path("data/images_material")
        template_dir.mkdir(exist_ok=True)
        
        # 创建测试图像
        img1 = np.zeros((200, 200, 3), dtype=np.uint8)
        cv2.rectangle(img1, (50, 50), (150, 150), (255, 0, 0), -1)
        cv2.putText(img1, "Test Product", (60, 120),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # 保存模板
        cv2.imwrite(str(template_dir / "test_product.jpg"), img1)
        print("✓ 创建测试模板")
        
        # 添加模板
        matcher.add_template("test_product", img1)
        
        # 创建查询图像（稍微不同的图像）
        img2 = np.zeros((300, 300, 3), dtype=np.uint8)
        cv2.rectangle(img2, (100, 100), (200, 200), (255, 0, 0), -1)
        
        # 匹配
        matches = matcher.match(img2)
        
        if matches:
            print(f"✓ 匹配成功: {matches[0]['template_name']}")
            print(f"  匹配点数: {matches[0]['match_count']}")
            
            # 显示结果
            result_img = matcher.draw_matches(img2, matches[0])
            cv2.imshow("匹配结果", result_img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        else:
            print("✗ 没有匹配")
        
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == "__main__":
    main()
    input("\n按Enter键退出...")
#!/usr/bin/env python3
"""
直播商品识别系统 - 主程序
双击即可运行
"""
import sys
import os
import cv2
import numpy as np
from pathlib import Path

def main_menu():
    """主菜单"""
    print("=" * 50)
    print("      直播商品识别系统 4.1")
    print("=" * 50)
    
    while True:
        print("\n请选择功能:")
        print("1. 实时商品检测")
        print("2. 图像匹配识别")
        print("3. 视频文件处理")
        print("4. 屏幕校准")
        print("5. 素材管理")
        print("6. 退出程序")
        
        choice = input("\n请输入选项 (1-6): ").strip()
        
        if choice == "1":
            realtime_detection()
        elif choice == "2":
            image_matching()
        elif choice == "3":
            video_processing()
        elif choice == "4":
            screen_calibration()
        elif choice == "5":
            material_management()
        elif choice == "6":
            print("\n感谢使用，再见！")
            break
        else:
            print("无效选项，请重新输入")

def realtime_detection():
    """实时商品检测"""
    print("\n[实时商品检测]")
    print("按 'q' 退出，按 's' 保存截图")
    
    try:
        # 尝试多个摄像头索引
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
        
        print("摄像头已打开，开始检测...")
        
        frame_count = 0
        detection_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # 简单的检测逻辑
            h, w = frame.shape[:2]
            center_x, center_y = w // 2, h // 2
            size = min(w, h) // 4
            
            # 绘制检测框
            cv2.rectangle(frame, 
                         (center_x - size//2, center_y - size//2),
                         (center_x + size//2, center_y + size//2),
                         (0, 255, 0), 2)
            
            # 添加标签
            label = "检测到商品"
            cv2.putText(frame, label, 
                       (center_x - size//2, center_y - size//2 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # 显示帧率
            cv2.putText(frame, f"Frame: {frame_count}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            cv2.imshow('实时商品检测 - 按q退出', frame)
            
            # 按键处理
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                # 保存截图
                import time
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"outputs/realtime_{timestamp}.jpg"
                Path("outputs").mkdir(exist_ok=True)
                cv2.imwrite(filename, frame)
                print(f"截图已保存: {filename}")
                detection_count += 1
        
        cap.release()
        cv2.destroyAllWindows()
        
        print(f"检测结束，共处理 {frame_count} 帧，检测到 {detection_count} 个商品")
        
    except Exception as e:
        print(f"实时检测出错: {e}")

def image_matching():
    """图像匹配识别"""
    print("\n[图像匹配识别]")
    
    try:
        from image_matcher import ImageMatcher
        print("图像匹配器加载成功")
        
        # 创建匹配器
        matcher = ImageMatcher()
        
        # 加载模板
        template_dir = Path("data/images_material")
        if template_dir.exists():
            count = matcher.load_templates_from_dir(template_dir)
            print(f"加载了 {count} 个模板")
        else:
            print("模板目录不存在: data/images_material/")
            print("已创建目录，请放入商品图片")
            template_dir.mkdir(parents=True, exist_ok=True)
            return
        
        # 选择输入图像
        print("\n选择输入方式:")
        print("1. 使用摄像头拍摄")
        print("2. 从文件选择图像")
        
        input_choice = input("请选择 (1-2): ").strip()
        
        if input_choice == "1":
            # 使用摄像头
            image = capture_from_camera()
            if image is None:
                return
        elif input_choice == "2":
            # 从文件选择
            image_path = select_image_file()
            if image_path is None:
                return
            image = cv2.imread(str(image_path))
            if image is None:
                print("无法读取图像文件")
                return
        else:
            print("无效选择")
            return
        
        # 进行匹配
        print("正在进行图像匹配...")
        matches = matcher.match(image)
        
        if matches:
            print(f"\n找到 {len(matches)} 个匹配:")
            for i, match in enumerate(matches[:3]):  # 显示前3个
                print(f"{i+1}. {match['template_name']} - "
                      f"{match['match_count']} 个匹配点")
            
            # 显示最佳匹配结果
            best_match = matches[0]
            result_img = matcher.draw_matches(image, best_match)
            cv2.imshow("图像匹配结果", result_img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        else:
            print("没有找到匹配的商品")
        
    except ImportError as e:
        print(f"无法导入图像匹配器: {e}")
    except Exception as e:
        print(f"图像匹配出错: {e}")

def capture_from_camera():
    """从摄像头捕获图像"""
    # 尝试多个摄像头索引
    for camera_id in [0, 1, 2]:
        cap = cv2.VideoCapture(camera_id)
        if cap.isOpened():
            print(f"打开摄像头 {camera_id}")
            break
        else:
            cap.release()
    else:
        print("无法打开任何摄像头")
        return None
    
    print("按 'c' 捕获图像，按 'q' 退出")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 显示预览
        preview = frame.copy()
        cv2.putText(preview, "按 'c' 捕获，'q' 退出", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.imshow("摄像头预览", preview)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('c'):
            cap.release()
            cv2.destroyAllWindows()
            return frame
    
    cap.release()
    cv2.destroyAllWindows()
    return None

def select_image_file():
    """选择图像文件"""
    try:
        import tkinter as tk
        from tkinter import filedialog
        
        root = tk.Tk()
        root.withdraw()
        
        file_path = filedialog.askopenfilename(
            title="选择图像文件",
            filetypes=[("图像文件", "*.jpg *.jpeg *.png *.bmp")]
        )
        
        if file_path:
            return Path(file_path)
        else:
            print("未选择文件")
            return None
            
    except ImportError:
        # 如果没有tkinter，使用简单输入
        file_path = input("请输入图像文件路径: ").strip()
        if os.path.exists(file_path):
            return Path(file_path)
        else:
            print("文件不存在")
            return None

def video_processing():
    """视频文件处理"""
    print("\n[视频文件处理]")
    
    try:
        from video_matcher import VideoMatcher
        
        # 创建视频匹配器
        matcher = VideoMatcher()
        
        # 加载模板
        template_dir = Path("data/images_material")
        if template_dir.exists():
            count = matcher.load_templates(template_dir)
            print(f"加载了 {count} 个模板")
        else:
            print("模板目录不存在")
            return
        
        # 选择视频文件
        print("\n请将视频文件放入 'data/videos' 目录")
        video_dir = Path("data/videos")
        if not video_dir.exists():
            print("视频目录不存在，已创建")
            video_dir.mkdir(parents=True, exist_ok=True)
            return
        
        video_files = list(video_dir.glob("*.mp4")) + \
                     list(video_dir.glob("*.avi")) + \
                     list(video_dir.glob("*.mov"))
        
        if not video_files:
            print("未找到视频文件")
            return
        
        print("\n找到的视频文件:")
        for i, video_file in enumerate(video_files, 1):
            print(f"{i}. {video_file.name}")
        
        choice = input(f"\n请选择文件 (1-{len(video_files)}): ").strip()
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(video_files):
                video_path = video_files[idx]
            else:
                print("无效选择")
                return
        except:
            print("无效选择")
            return
        
        print(f"开始处理视频: {video_path.name}")
        print("按 'q' 可以提前退出")
        
        # 处理视频
        matcher.process_video_file(video_path, show_preview=True)
        
    except ImportError as e:
        print(f"无法导入视频匹配器: {e}")
    except Exception as e:
        print(f"视频处理出错: {e}")

def screen_calibration():
    """屏幕校准"""
    print("\n[屏幕校准]")
    
    try:
        from calibrate_region import Calibrator
        calibrator = Calibrator()
        calibrator.run()
    except ImportError as e:
        print(f"无法导入校准模块: {e}")
        simple_calibration()

def simple_calibration():
    """简单屏幕校准"""
    print("简单屏幕校准模式")
    print("提示: 选择屏幕捕获区域")
    
    try:
        import cv2
        
        # 创建一个黑色图像作为校准背景
        calib_img = np.zeros((500, 800, 3), dtype=np.uint8)
        
        # 添加说明文字
        cv2.putText(calib_img, "屏幕校准", (300, 100),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(calib_img, "用鼠标拖动选择区域，按Enter确认", (200, 150),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # 选择区域
        roi = cv2.selectROI("屏幕校准", calib_img, False)
        cv2.destroyAllWindows()
        
        if roi[2] > 0 and roi[3] > 0:
            print(f"选择的区域: x={roi[0]}, y={roi[1]}, 宽={roi[2]}, 高={roi[3]}")
            
            # 保存配置
            import yaml
            config = {
                'screen_region': {
                    'x': int(roi[0]),
                    'y': int(roi[1]),
                    'width': int(roi[2]),
                    'height': int(roi[3])
                }
            }
            
            Path("config").mkdir(exist_ok=True)
            with open("config/calibration.yaml", "w") as f:
                yaml.dump(config, f)
            
            print("校准配置已保存")
        else:
            print("校准取消")
            
    except Exception as e:
        print(f"屏幕校准出错: {e}")

def material_management():
    """素材管理"""
    print("\n[素材管理]")
    
    try:
        from check_materials import check_materials
        check_materials()
    except ImportError as e:
        print(f"无法导入素材检查模块: {e}")
        simple_material_check()

def simple_material_check():
    """简单素材检查"""
    print("简单素材检查")
    
    directories = [
        ("图像素材", "data/images_material"),
        ("视频素材", "data/videos_material"),
        ("输出目录", "outputs"),
        ("配置目录", "config")
    ]
    
    for name, path in directories:
        dir_path = Path(path)
        if dir_path.exists():
            files = list(dir_path.glob("*.*"))
            print(f"✓ {name}: {len(files)} 个文件")
        else:
            print(f"✗ {name}: 目录不存在")
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"  已创建目录")

def main():
    """主函数"""
    # 创建必要的目录
    os.makedirs("data/images_material", exist_ok=True)
    os.makedirs("data/videos_material", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)
    os.makedirs("config", exist_ok=True)
    
    # 运行主菜单
    main_menu()
    
    input("\n按Enter键退出程序...")

if __name__ == "__main__":
    main()
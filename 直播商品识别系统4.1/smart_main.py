#!/usr/bin/env python3
"""
智能主程序 - 集成自动学习功能（修复版）
"""
import sys
import os
import cv2
import numpy as np
from pathlib import Path

# 导入工具模块
sys.path.append('.')  # 添加当前目录到路径
from utils.image_utils import read_image, save_image, resize_image
from utils.file_dialog import select_image_file, select_directory
from auto_learner import SmartLearningSystem
from output_manager import get_output_manager

def main():
    print("=" * 60)
    print("        直播商品识别系统 - 智能版")
    print("                    🤖 带自动学习功能")
    print("=" * 60)
    
    # 初始化输出管理器
    output_mgr = get_output_manager()
    output_mgr.log_system("Main", "程序启动")
    
    # 创建必要的目录
    os.makedirs("data/images_material", exist_ok=True)
    os.makedirs("data/learned_samples", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)
    os.makedirs("utils", exist_ok=True)
    
    # 创建智能学习系统
    print("初始化智能学习系统...")
    learning_system = SmartLearningSystem()
    
    try:
        while True:
            print("\n请选择功能:")
            print("1. 智能实时检测 (带自动学习)")
            print("2. 图像匹配识别")
            print("3. 手动学习新商品")
            print("4. 查看学习统计")
            print("5. 自动学习演示")
            print("6. 系统设置")
            print("7. 退出程序")
            
            choice = input("\n请输入选项 (1-7): ").strip()
            output_mgr.log_system("MainMenu", f"用户选择: {choice}")
            
            if choice == "1":
                smart_realtime_detection(learning_system, output_mgr)
            elif choice == "2":
                image_matching(learning_system, output_mgr)
            elif choice == "3":
                manual_learning(learning_system, output_mgr)
            elif choice == "4":
                show_learning_stats(learning_system, output_mgr)
            elif choice == "5":
                auto_learning_demo(learning_system, output_mgr)
            elif choice == "6":
                system_settings(learning_system, output_mgr)
            elif choice == "7":
                print("\n感谢使用，再见！")
                output_mgr.log_system("Main", "程序退出")
                break
            else:
                print("无效选项，请重新输入")
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        output_mgr.log_system("Main", "程序被用户中断", "WARNING")
    except Exception as e:
        error_msg = f"程序运行出错: {e}"
        print(error_msg)
        output_mgr.log_system("Main", error_msg, "ERROR")
        import traceback
        traceback.print_exc()

def smart_realtime_detection(learning_system, output_mgr):
    """智能实时检测（带自动学习）"""
    print("\n[智能实时检测 - 带自动学习]")
    print("按 'q' 退出，按 's' 保存截图，按 'l' 手动学习")
    
    output_mgr.log_system("SmartRealTimeDetection", "开始智能实时检测")
    
    # 打开摄像头
    cap = open_camera(output_mgr)
    if cap is None:
        return
    
    frame_count = 0
    auto_learned_count = 0
    
    print("开始检测...")
    print("提示: 系统会自动学习未知商品")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # 使用智能系统处理帧
            results = learning_system.process_frame(frame)
            
            # 准备显示帧
            display_frame = frame.copy()
            h, w = display_frame.shape[:2]
            
            # 显示匹配结果
            if results.get('match_results'):
                best_match = results['match_results'][0]
                match_text = f"匹配: {best_match['template_name']} ({best_match['quality']:.2f})"
                color = (0, 255, 0)  # 绿色
                
                # 更新当前商品
                output_mgr.update_current_product(
                    best_match['template_name'],
                    best_match['quality'],
                    frame_info=f"摄像头 {w}x{h}"
                )
            else:
                match_text = "未知商品"
                color = (0, 0, 255)  # 红色
            
            # 显示状态
            status_lines = [
                match_text,
                f"帧数: {frame_count}",
                f"自动学习: {results['stats']['auto_learned_count']}",
                f"手动学习: {results['stats']['manual_learned_count']}"
            ]
            
            # 如果有自动学习发生
            if results.get('learned'):
                status_lines.append(f"🎯 已学习: {results['learned_item']['name']}")
                auto_learned_count += 1
            
            # 绘制状态信息
            y_offset = 30
            for line in status_lines:
                cv2.putText(display_frame, line, (10, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                y_offset += 25
            
            # 绘制检测区域
            cv2.rectangle(display_frame, 
                         (w//4, h//4), 
                         (3*w//4, 3*h//4), 
                         (0, 255, 0), 2)
            
            cv2.imshow('智能实时检测 - 按q退出', display_frame)
            
            # 按键处理
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                # 保存截图
                import time
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"outputs/smart_{timestamp}.jpg"
                save_image(display_frame, filename)
                print(f"截图已保存: {filename}")
                output_mgr.log_system("SmartRealTimeDetection", f"保存截图: {filename}")
            elif key == ord('l'):
                # 手动学习当前帧
                success, item_info = learning_system.manual_learn(frame)
                if success:
                    print(f"手动学习完成: {item_info['name']}")
                    output_mgr.log_system("SmartRealTimeDetection", f"手动学习: {item_info['name']}")
    
    except KeyboardInterrupt:
        print("\n检测被用户中断")
        output_mgr.log_system("SmartRealTimeDetection", "检测被用户中断", "WARNING")
    except Exception as e:
        error_msg = f"检测出错: {e}"
        print(error_msg)
        output_mgr.log_system("SmartRealTimeDetection", error_msg, "ERROR")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        
        # 显示统计信息
        print(f"\n检测统计:")
        print(f"总帧数: {frame_count}")
        print(f"自动学习次数: {auto_learned_count}")
        
        # 保存统计信息到日志
        stats_msg = f"检测统计 - 总帧数: {frame_count}, 自动学习次数: {auto_learned_count}"
        output_mgr.log_system("SmartRealTimeDetection", stats_msg)
        
        # 保存学习数据
        learning_system.auto_learner._save_learning_data()
        output_mgr.log_system("SmartRealTimeDetection", "学习数据已保存")

def open_camera(output_mgr):
    """打开摄像头"""
    for camera_id in [0, 1, 2]:
        cap = cv2.VideoCapture(camera_id)
        if cap.isOpened():
            message = f"打开摄像头 {camera_id}"
            print(f"✓ {message}")
            output_mgr.log_system("OpenCamera", message)
            return cap
        cap.release()
    
    error_msg = "无法打开任何摄像头"
    print(error_msg)
    output_mgr.log_system("OpenCamera", error_msg, "ERROR")
    return None

def image_matching(learning_system, output_mgr):
    """图像匹配识别"""
    print("\n[图像匹配识别]")
    output_mgr.log_system("ImageMatching", "开始图像匹配识别")
    
    try:
        # 选择输入方式
        print("\n选择输入方式:")
        print("1. 使用摄像头拍摄")
        print("2. 从文件选择图像")
        
        input_choice = input("请选择 (1-2): ").strip()
        output_mgr.log_system("ImageMatching", f"输入方式选择: {input_choice}")
        
        if input_choice == "1":
            # 使用摄像头
            frame = capture_from_camera(output_mgr)
            if frame is None:
                return
        elif input_choice == "2":
            # 从文件选择
            frame = load_image_from_file(output_mgr)
            if frame is None:
                return
        else:
            print("无效选择")
            return
        
        # 进行匹配
        print("正在进行图像匹配...")
        matches = learning_system.image_matcher.match(frame)
        
        if matches:
            print(f"\n找到 {len(matches)} 个匹配:")
            for i, match in enumerate(matches[:3]):
                print(f"{i+1}. {match['template_name']} - "
                      f"{match['match_count']} 个匹配点 (置信度: {match['quality']:.2f})")
            
            # 记录匹配结果
            best_match = matches[0]
            match_msg = f"找到匹配: {best_match['template_name']} (置信度: {best_match['quality']:.2f})"
            output_mgr.log_recognition(best_match['template_name'], best_match['quality'])
            output_mgr.log_system("ImageMatching", match_msg)
            
            # 显示最佳匹配结果
            result_img = learning_system.image_matcher.draw_matches(frame, best_match)
            cv2.imshow("图像匹配结果", result_img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        else:
            print("没有找到匹配的商品")
            output_mgr.log_system("ImageMatching", "未找到匹配的商品", "INFO")
            
            # 询问是否学习这个商品
            choice = input("是否学习这个新商品? (y/n): ").lower()
            if choice == 'y':
                output_mgr.log_system("ImageMatching", "用户选择学习新商品", "INFO")
                success, item_info = learning_system.manual_learn(frame)
                if success:
                    print(f"已学习新商品: {item_info['name']}")
                    output_mgr.log_system("ImageMatching", f"已学习新商品: {item_info['name']}")
        
    except Exception as e:
        error_msg = f"图像匹配出错: {e}"
        print(error_msg)
        output_mgr.log_system("ImageMatching", error_msg, "ERROR")

def load_image_from_file(output_mgr):
    """从文件加载图像"""
    print("请选择图像文件...")
    
    # 使用文件对话框选择文件
    image_path = select_image_file("选择要识别的图像")
    
    if image_path is None:
        print("未选择文件")
        output_mgr.log_system("LoadImageFromFile", "用户未选择文件", "WARNING")
        return None
    
    print(f"正在加载: {image_path}")
    output_mgr.log_system("LoadImageFromFile", f"加载图像: {image_path}")
    
    # 使用工具函数读取图像（支持中文路径）
    frame = read_image(image_path)
    
    if frame is None:
        error_msg = "无法读取图像文件，请检查文件格式和路径"
        print(error_msg)
        output_mgr.log_system("LoadImageFromFile", error_msg, "ERROR")
        return None
    
    print(f"图像加载成功，尺寸: {frame.shape[1]}x{frame.shape[0]}")
    output_mgr.log_system("LoadImageFromFile", 
                         f"图像加载成功，尺寸: {frame.shape[1]}x{frame.shape[0]}")
    return frame

def capture_from_camera(output_mgr):
    """从摄像头捕获图像"""
    cap = open_camera(output_mgr)
    if cap is None:
        return None
    
    print("按 'c' 捕获图像，按 'q' 退出")
    output_mgr.log_system("CaptureFromCamera", "开始摄像头捕获")
    
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
            output_mgr.log_system("CaptureFromCamera", "用户取消捕获", "INFO")
            break
        elif key == ord('c'):
            output_mgr.log_system("CaptureFromCamera", "用户捕获图像", "INFO")
            cap.release()
            cv2.destroyAllWindows()
            return frame
    
    cap.release()
    cv2.destroyAllWindows()
    return None

def manual_learning(learning_system, output_mgr):
    """手动学习新商品"""
    print("\n[手动学习新商品]")
    output_mgr.log_system("ManualLearning", "开始手动学习新商品")
    
    try:
        print("请准备要学习的商品...")
        
        # 选择输入方式
        print("\n选择输入方式:")
        print("1. 使用摄像头拍摄")
        print("2. 从文件选择图像")
        
        input_choice = input("请选择 (1-2): ").strip()
        output_mgr.log_system("ManualLearning", f"输入方式选择: {input_choice}")
        
        if input_choice == "1":
            # 使用摄像头
            frame = capture_from_camera(output_mgr)
            if frame is None:
                return
        elif input_choice == "2":
            # 从文件选择
            frame = load_image_from_file(output_mgr)
            if frame is None:
                return
        else:
            print("无效选择")
            return
        
        # 输入商品名称
        item_name = input("请输入商品名称 (直接回车使用自动命名): ").strip()
        if not item_name:
            item_name = None
            output_mgr.log_system("ManualLearning", "使用自动命名")
        
        # 显示预览
        preview = frame.copy()
        preview = resize_image(preview, max_size=600)
        cv2.imshow("学习预览 - 按任意键继续", preview)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        # 手动学习
        success, item_info = learning_system.manual_learn(frame, item_name)
        
        if success:
            print(f"✅ 手动学习完成: {item_info['name']}")
            print(f"   保存位置: {item_info['image_path']}")
            
            # 记录学习日志
            output_mgr.log_system("ManualLearning", f"手动学习完成: {item_info['name']}")
            
            # 询问是否立即测试
            choice = input("是否立即测试学习效果? (y/n): ").lower()
            if choice == 'y':
                output_mgr.log_system("ManualLearning", "用户选择立即测试学习效果", "INFO")
                test_learned_item(learning_system, item_info['name'], output_mgr)
        else:
            error_msg = "❌ 手动学习失败"
            print(error_msg)
            output_mgr.log_system("ManualLearning", error_msg, "ERROR")
            
    except Exception as e:
        error_msg = f"手动学习出错: {e}"
        print(error_msg)
        output_mgr.log_system("ManualLearning", error_msg, "ERROR")

def test_learned_item(learning_system, item_name, output_mgr):
    """测试学习到的商品"""
    print(f"\n测试学习到的商品: {item_name}")
    output_mgr.log_system("TestLearnedItem", f"开始测试学习到的商品: {item_name}")
    
    print("请向摄像头展示刚才学习的商品...")
    
    cap = open_camera(output_mgr)
    if cap is None:
        return
    
    print("按任意键开始测试，按 'q' 退出")
    
    test_frames = 0
    matched_frames = 0
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # 显示预览
            preview = frame.copy()
            cv2.putText(preview, f"测试: {item_name}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(preview, "按任意键开始测试，按 'q' 退出", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            cv2.imshow("测试学习效果", preview)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                output_mgr.log_system("TestLearnedItem", "用户退出测试", "INFO")
                break
            elif key != 255:  # 任意其他键
                # 开始测试
                print("开始测试...")
                test_frames += 1
                
                # 进行匹配
                matches = learning_system.image_matcher.match(frame)
                if matches:
                    best_match = matches[0]
                    if best_match['template_name'] == item_name:
                        matched_frames += 1
                        print(f"  第 {test_frames} 帧: ✓ 匹配成功 (置信度: {best_match['quality']:.2f})")
                        output_mgr.log_recognition(item_name, best_match['quality'], test_mode=True)
                    else:
                        print(f"  第 {test_frames} 帧: ✗ 匹配到其他商品: {best_match['template_name']}")
                        output_mgr.log_system("TestLearnedItem", 
                                            f"第 {test_frames} 帧: 匹配到其他商品: {best_match['template_name']}", 
                                            "WARNING")
                else:
                    print(f"  第 {test_frames} 帧: ✗ 未匹配到任何商品")
                    output_mgr.log_system("TestLearnedItem", 
                                        f"第 {test_frames} 帧: 未匹配到任何商品", 
                                        "WARNING")
                
                # 显示几帧后自动结束
                if test_frames >= 10:
                    output_mgr.log_system("TestLearnedItem", "达到测试帧数上限，结束测试", "INFO")
                    break
    
    except Exception as e:
        error_msg = f"测试学习商品出错: {e}"
        print(error_msg)
        output_mgr.log_system("TestLearnedItem", error_msg, "ERROR")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        
        if test_frames > 0:
            accuracy = matched_frames / test_frames * 100
            print(f"\n测试结果:")
            print(f"  测试帧数: {test_frames}")
            print(f"  匹配帧数: {matched_frames}")
            print(f"  准确率: {accuracy:.1f}%")
            
            # 记录测试结果
            test_result = f"测试结果 - 测试帧数: {test_frames}, 匹配帧数: {matched_frames}, 准确率: {accuracy:.1f}%"
            output_mgr.log_system("TestLearnedItem", test_result)

def show_learning_stats(learning_system, output_mgr):
    """显示学习统计"""
    print("\n[学习统计信息]")
    output_mgr.log_system("ShowLearningStats", "查看学习统计信息")
    
    try:
        stats = learning_system.get_learning_summary()
        
        print("=" * 50)
        print("📊 学习统计")
        print("=" * 50)
        print(f"总处理帧数: {stats['total_processed_frames']}")
        print(f"自动学习次数: {stats['auto_learned_count']}")
        print(f"手动学习次数: {stats['manual_learned_count']}")
        print(f"总学习商品数: {stats['total_learned']}")
        print(f"当前模板数: {stats['current_templates']}")
        print(f"学习历史记录: {stats['learning_history_count']}")
        print(f"最后学习商品: {stats['last_learned_item']}")
        print(f"学习功能: {'启用' if stats['learning_enabled'] else '禁用'}")
        print(f"模板目录: {stats['template_dir']}")
        print("=" * 50)
        
        # 记录统计信息
        stats_message = (
            f"学习统计: "
            f"总处理帧数: {stats['total_processed_frames']}, "
            f"自动学习: {stats['auto_learned_count']}, "
            f"手动学习: {stats['manual_learned_count']}, "
            f"总学习商品: {stats['total_learned']}"
        )
        output_mgr.log_system("ShowLearningStats", stats_message)
        
        # 显示最近学习的商品
        if learning_system.auto_learner.learned_items:
            print("\n最近学习的商品:")
            recent_items = learning_system.auto_learner.learned_items[-5:]  # 最近5个
            for i, item in enumerate(reversed(recent_items), 1):
                print(f"  {i}. {item['name']} - {item['learned_at'][:16]}")
        
        # 询问是否合并学习数据
        choice = input("\n是否将学习数据合并到模板库? (y/n): ").lower()
        if choice == 'y':
            output_mgr.log_system("ShowLearningStats", "用户选择合并学习数据到模板库", "INFO")
            merged = learning_system.auto_learner.merge_with_templates("data/images_material")
            print(f"✅ 已合并 {merged} 个商品到模板库")
            output_mgr.log_system("ShowLearningStats", f"已合并 {merged} 个商品到模板库")
    except Exception as e:
        error_msg = f"显示学习统计出错: {e}"
        print(error_msg)
        output_mgr.log_system("ShowLearningStats", error_msg, "ERROR")

def auto_learning_demo(learning_system, output_mgr):
    """自动学习演示"""
    print("\n[自动学习演示]")
    output_mgr.log_system("AutoLearningDemo", "开始自动学习演示")
    
    try:
        duration = input("请输入演示时长(秒，默认30秒): ").strip()
        if duration:
            try:
                duration_seconds = int(duration)
            except:
                duration_seconds = 30
                print("输入无效，使用默认值30秒")
        else:
            duration_seconds = 30
        
        output_mgr.log_system("AutoLearningDemo", f"演示时长: {duration_seconds}秒")
        learning_system.run_auto_learning_demo(duration_seconds=duration_seconds)
        output_mgr.log_system("AutoLearningDemo", "自动学习演示完成")
    except Exception as e:
        error_msg = f"演示出错: {e}"
        print(error_msg)
        output_mgr.log_system("AutoLearningDemo", error_msg, "ERROR")

def system_settings(learning_system, output_mgr):
    """系统设置"""
    print("\n[系统设置]")
    output_mgr.log_system("SystemSettings", "进入系统设置")
    
    while True:
        print("\n系统设置选项:")
        print("1. 查看和修改学习参数")
        print("2. 清理学习数据")
        print("3. 备份学习数据")
        print("4. 恢复学习数据")
        print("5. 返回主菜单")
        
        choice = input("\n请选择 (1-5): ").strip()
        output_mgr.log_system("SystemSettings", f"用户选择: {choice}")
        
        if choice == "1":
            learning_settings(learning_system, output_mgr)
        elif choice == "2":
            cleanup_learning_data(learning_system, output_mgr)
        elif choice == "3":
            backup_learning_data(learning_system, output_mgr)
        elif choice == "4":
            restore_learning_data(learning_system, output_mgr)
        elif choice == "5":
            output_mgr.log_system("SystemSettings", "退出系统设置")
            break
        else:
            print("无效选项")

def learning_settings(learning_system, output_mgr):
    """学习参数设置"""
    print("\n[学习参数设置]")
    output_mgr.log_system("LearningSettings", "进入学习参数设置")
    
    print(f"当前参数:")
    print(f"  学习功能: {'启用' if learning_system.auto_learner.learning_enabled else '禁用'}")
    print(f"  最低置信度: {learning_system.auto_learner.min_confidence}")
    print(f"  学习阈值: {learning_system.auto_learner.learning_threshold}")
    print(f"  最大学习数量: {learning_system.auto_learner.max_learned_items}")
    
    print("\n修改参数:")
    print("1. 切换学习功能状态")
    print("2. 设置最低置信度")
    print("3. 设置学习阈值")
    print("4. 设置最大学习数量")
    print("5. 返回")
    
    choice = input("\n请选择 (1-5): ").strip()
    output_mgr.log_system("LearningSettings", f"参数修改选择: {choice}")
    
    if choice == "1":
        new_state = not learning_system.auto_learner.learning_enabled
        learning_system.auto_learner.learning_enabled = new_state
        message = f"学习功能已 {'启用' if new_state else '禁用'}"
        print(message)
        output_mgr.log_system("LearningSettings", message)
    elif choice == "2":
        try:
            value = float(input("请输入最低置信度 (0.0-1.0): "))
            if 0.0 <= value <= 1.0:
                learning_system.auto_learner.min_confidence = value
                message = f"最低置信度已设置为: {value}"
                print(message)
                output_mgr.log_system("LearningSettings", message)
            else:
                error_msg = "无效的值，必须介于0.0和1.0之间"
                print(error_msg)
                output_mgr.log_system("LearningSettings", error_msg, "WARNING")
        except:
            error_msg = "无效的输入"
            print(error_msg)
            output_mgr.log_system("LearningSettings", error_msg, "WARNING")
    elif choice == "3":
        try:
            value = float(input("请输入学习阈值 (0.0-1.0): "))
            if 0.0 <= value <= 1.0:
                learning_system.auto_learner.learning_threshold = value
                message = f"学习阈值已设置为: {value}"
                print(message)
                output_mgr.log_system("LearningSettings", message)
            else:
                error_msg = "无效的值，必须介于0.0和1.0之间"
                print(error_msg)
                output_mgr.log_system("LearningSettings", error_msg, "WARNING")
        except:
            error_msg = "无效的输入"
            print(error_msg)
            output_mgr.log_system("LearningSettings", error_msg, "WARNING")
    elif choice == "4":
        try:
            value = int(input("请输入最大学习数量: "))
            if value > 0:
                learning_system.auto_learner.max_learned_items = value
                message = f"最大学习数量已设置为: {value}"
                print(message)
                output_mgr.log_system("LearningSettings", message)
            else:
                error_msg = "无效的值，必须大于0"
                print(error_msg)
                output_mgr.log_system("LearningSettings", error_msg, "WARNING")
        except:
            error_msg = "无效的输入"
            print(error_msg)
            output_mgr.log_system("LearningSettings", error_msg, "WARNING")
    elif choice == "5":
        output_mgr.log_system("LearningSettings", "返回系统设置菜单")

# 其他辅助函数...
def cleanup_learning_data(learning_system, output_mgr):
    """清理学习数据"""
    print("\n[清理学习数据]")
    output_mgr.log_system("CleanupLearningData", "开始清理学习数据")
    
    confirm = input("确认清理学习数据? 这将删除所有已学习但未合并的样本 (y/n): ").lower()
    if confirm == 'y':
        try:
            learning_system.auto_learner.cleanup_learning_data()
            print("✅ 学习数据已清理")
            output_mgr.log_system("CleanupLearningData", "学习数据已清理")
        except Exception as e:
            error_msg = f"清理学习数据失败: {e}"
            print(error_msg)
            output_mgr.log_system("CleanupLearningData", error_msg, "ERROR")

def backup_learning_data(learning_system, output_mgr):
    """备份学习数据"""
    print("\n[备份学习数据]")
    output_mgr.log_system("BackupLearningData", "开始备份学习数据")
    
    try:
        learning_system.auto_learner.backup_learning_data()
        print("✅ 学习数据已备份")
        output_mgr.log_system("BackupLearningData", "学习数据已备份")
    except Exception as e:
        error_msg = f"备份学习数据失败: {e}"
        print(error_msg)
        output_mgr.log_system("BackupLearningData", error_msg, "ERROR")

def restore_learning_data(learning_system, output_mgr):
    """恢复学习数据"""
    print("\n[恢复学习数据]")
    output_mgr.log_system("RestoreLearningData", "开始恢复学习数据")
    
    confirm = input("确认恢复学习数据? 这将覆盖当前的学习数据 (y/n): ").lower()
    if confirm == 'y':
        try:
            learning_system.auto_learner.restore_learning_data()
            print("✅ 学习数据已恢复")
            output_mgr.log_system("RestoreLearningData", "学习数据已恢复")
        except Exception as e:
            error_msg = f"恢复学习数据失败: {e}"
            print(error_msg)
            output_mgr.log_system("RestoreLearningData", error_msg, "ERROR")

if __name__ == "__main__":
    main()
    input("\n按Enter键退出程序...")
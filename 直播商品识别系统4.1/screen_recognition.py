#!/usr/bin/env python3
"""
屏幕视频识别系统
专门用于识别桌面播放的视频内容
"""
import sys
import os
import cv2
import numpy as np
import time
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append('.')

from screen_capture import ScreenCapture
from auto_learner import SmartLearningSystem
from utils.image_utils import read_image, save_image
from output_manager import get_output_manager

class ScreenRecognitionSystem:
    def __init__(self, config_path="config/screen_config.yaml"):
        """
        初始化屏幕识别系统
        
        参数:
            config_path: 配置文件路径
        """
        print("=" * 60)
        print("        屏幕视频识别系统")
        print("=" * 60)
        
        # 初始化输出管理器
        self.output_mgr = get_output_manager()
        self.output_mgr.log_system("ScreenRecognition", "系统初始化开始")
        
        # 加载配置
        self.config = self._load_config(config_path)
        
        # 初始化屏幕捕获器
        self.screen_capture = self._init_screen_capture()
        
        # 初始化智能学习系统
        self.learning_system = SmartLearningSystem()
        
        # 状态变量
        self.is_running = False
        self.recognition_stats = {
            'total_frames': 0,
            'matched_frames': 0,
            'learned_items': 0,
            'start_time': None,
            'current_product': None
        }
        
        self.output_mgr.log_system("ScreenRecognition", "系统初始化完成")
        print("✅ 屏幕识别系统初始化完成")
    
    def _load_config(self, config_path):
        """加载配置文件"""
        config_file = Path(config_path)
        
        if not config_file.exists():
            print(f"配置文件不存在，创建默认配置: {config_path}")
            return self._create_default_config(config_path)
        
        try:
            import yaml
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            error_msg = f"加载配置失败: {e}"
            self.output_mgr.log_system("_load_config", error_msg, "ERROR")
            print(f"{error_msg}，使用默认配置")
            return {}
    
    def _create_default_config(self, config_path):
        """创建默认配置"""
        config = {
            'screen': {
                'capture_method': 'mss',
                'fps': 10,
                'region': 'full_screen',
                'auto_calibrate': True
            },
            'recognition': {
                'auto_learn': True,
                'min_confidence': 0.3,
                'save_matches': True,
                'match_interval': 1  # 匹配间隔(秒)
            },
            'output': {
                'save_dir': 'outputs/screen_matches',
                'save_format': 'jpg',
                'max_saves_per_item': 10
            }
        }
        
        # 保存配置
        Path("config").mkdir(exist_ok=True)
        try:
            import yaml
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            
            self.output_mgr.log_system("_create_default_config", 
                                     f"默认配置已创建: {config_path}")
            print(f"默认配置已创建: {config_path}")
        except Exception as e:
            error_msg = f"创建默认配置失败: {e}"
            self.output_mgr.log_system("_create_default_config", error_msg, "ERROR")
            print(error_msg)
        
        return config
    
    def _init_screen_capture(self):
        """初始化屏幕捕获器"""
        try:
            # 获取配置
            screen_config = self.config.get('screen', {})
            capture_method = screen_config.get('capture_method', 'mss')
            
            # 创建捕获器
            capture = ScreenCapture(capture_method=capture_method)
            
            # 加载校准配置
            if not capture.load_calibration():
                self.output_mgr.log_system("_init_screen_capture", "未找到校准配置")
                print("未找到校准配置")
                
                # 如果配置要求自动校准
                if screen_config.get('auto_calibrate', True):
                    print("开始自动校准...")
                    self.output_mgr.log_system("_init_screen_capture", "开始自动校准")
                    capture.calibrate_region()
            
            return capture
        except Exception as e:
            error_msg = f"初始化屏幕捕获器失败: {e}"
            self.output_mgr.log_system("_init_screen_capture", error_msg, "ERROR")
            raise Exception(error_msg)
    
    def run(self):
        """运行屏幕识别系统"""
        print("\n🚀 启动屏幕识别系统")
        self.output_mgr.log_system("ScreenRecognition", "启动屏幕识别系统")
        
        # 显示配置
        self.show_config_summary()
        
        # 加载模板
        self._load_templates()
        
        # 显示菜单
        self.main_menu()
    
    def show_config_summary(self):
        """显示配置摘要"""
        print("\n📋 当前配置:")
        print("-" * 40)
        
        screen_config = self.config.get('screen', {})
        recog_config = self.config.get('recognition', {})
        
        # 获取屏幕区域
        region = self.screen_capture.region
        if region:
            region_text = f"区域: {region[0]},{region[1]}({region[2]}x{region[3]})"
        else:
            region_text = "区域: 全屏"
        
        print(f"屏幕捕获: {screen_config.get('capture_method', 'mss')}")
        print(region_text)
        print(f"帧率: {screen_config.get('fps', 10)} FPS")
        print(f"自动学习: {'启用' if recog_config.get('auto_learn', True) else '禁用'}")
        print(f"最小置信度: {recog_config.get('min_confidence', 0.3)}")
        print("-" * 40)
    
    def main_menu(self):
        """主菜单"""
        while True:
            print("\n请选择功能:")
            print("1. 开始屏幕识别")
            print("2. 屏幕区域校准")
            print("3. 模板管理")
            print("4. 识别设置")
            print("5. 快速测试")
            print("6. 返回主系统")
            
            choice = input("\n请输入选项 (1-6): ").strip()
            
            if choice == "1":
                self.start_recognition()
            elif choice == "2":
                self.calibrate_screen()
            elif choice == "3":
                self.template_management()
            elif choice == "4":
                self.recognition_settings()
            elif choice == "5":
                self.quick_test()
            elif choice == "6":
                print("返回主系统...")
                self.output_mgr.log_system("ScreenRecognition", "返回主系统")
                break
            else:
                print("无效选项")
                self.output_mgr.log_system("main_menu", f"无效选项: {choice}", "WARNING")
    
    def start_recognition(self):
        """开始屏幕识别"""
        print("\n[开始屏幕识别]")
        print("提示: 请在桌面上播放要识别的视频")
        print("快捷键:")
        print("  q - 退出识别")
        print("  s - 保存当前帧")
        print("  l - 手动学习当前商品")
        print("  c - 切换显示模式")
        print("  p - 暂停/继续")
        
        self.output_mgr.log_system("ScreenRecognition", "开始屏幕识别")
        
        # 获取配置
        screen_config = self.config.get('screen', {})
        recog_config = self.config.get('recognition', {})
        
        fps = screen_config.get('fps', 10)
        match_interval = recog_config.get('match_interval', 1)
        
        # 初始化状态
        self.is_running = True
        self.recognition_stats['start_time'] = time.time()
        self.recognition_stats['total_frames'] = 0
        self.recognition_stats['matched_frames'] = 0
        
        last_match_time = 0
        display_mode = 'normal'  # normal, debug, minimal
        is_paused = False
        
        try:
            # 开始捕获
            for frame in self.screen_capture.start_capture(fps=fps):
                if not self.is_running or frame is None:
                    break
                
                if is_paused:
                    # 显示暂停状态
                    paused_frame = frame.copy()
                    cv2.putText(paused_frame, "⏸️ 暂停中", 
                               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                               1, (0, 0, 255), 2)
                    cv2.imshow('屏幕识别 - 暂停中 (按p继续)', paused_frame)
                    
                    key = cv2.waitKey(100)  # 暂停时较长的等待
                    if key == ord('p'):
                        is_paused = False
                        cv2.destroyAllWindows()
                    continue
                
                self.recognition_stats['total_frames'] += 1
                
                current_time = time.time()
                
                # 检查是否需要进行匹配
                if current_time - last_match_time >= match_interval:
                    # 进行识别
                    results = self.learning_system.process_frame(frame)
                    last_match_time = current_time
                    
                    # 更新统计
                    if results.get('match_results'):
                        self.recognition_stats['matched_frames'] += 1
                        best_match = results['match_results'][0]
                        self.recognition_stats['current_product'] = best_match['template_name']
                        
                        # 记录屏幕识别日志
                        product_name = best_match['template_name']
                        confidence = best_match['quality']
                        
                        self.output_mgr.log_screen_recognition(
                            product_name, 
                            confidence,
                            screen_region=str(self.screen_capture.region)
                        )
                        
                        # 更新当前商品
                        self.output_mgr.update_current_product(
                            f"[屏幕] {product_name}",
                            confidence,
                            frame_info=f"屏幕区域: {self.screen_capture.region}"
                        )
                    
                    # 自动学习
                    if recog_config.get('auto_learn', True) and results.get('learned'):
                        print(f"🤖 自动学习: {results['learned_item']['name']}")
                        # 自动学习已经通过learning_system记录了，这里可以添加额外处理
                else:
                    results = {'match_results': []}
                
                # 准备显示帧
                display_frame = self._prepare_display_frame(frame, results, display_mode)
                
                # 显示帧
                cv2.imshow('屏幕识别 - 按q退出', display_frame)
                
                # 按键处理
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    self._save_current_frame(frame, results)
                elif key == ord('l'):
                    self._manual_learn_current(frame, results)
                elif key == ord('c'):
                    display_mode = self._cycle_display_mode(display_mode)
                elif key == ord('p'):
                    is_paused = True
        
        except KeyboardInterrupt:
            print("\n识别被用户中断")
            self.output_mgr.log_system("start_recognition", "识别被用户中断")
        except Exception as e:
            error_msg = f"识别出错: {e}"
            self.output_mgr.log_system("start_recognition", error_msg, "ERROR")
            print(error_msg)
            import traceback
            traceback.print_exc()
        finally:
            self.is_running = False
            self.screen_capture.stop_capture()
            cv2.destroyAllWindows()
            
            # 显示统计信息
            self._show_recognition_stats()
            
            # 记录识别结束
            self.output_mgr.log_system("ScreenRecognition", "屏幕识别结束")
    
    def _prepare_display_frame(self, frame, results, mode='normal'):
        """准备显示帧"""
        display_frame = frame.copy()
        h, w = display_frame.shape[:2]
        
        if mode == 'minimal':
            # 最小化模式，只显示基本信息
            fps = self._calculate_fps()
            cv2.putText(display_frame, f"FPS: {fps:.1f}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
            
            if results.get('match_results'):
                best_match = results['match_results'][0]
                cv2.putText(display_frame, f"匹配: {best_match['template_name']}", 
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
        
        elif mode == 'debug':
            # 调试模式，显示详细信息
            fps = self._calculate_fps()
            
            info_lines = [
                f"帧: {self.recognition_stats['total_frames']}",
                f"FPS: {fps:.1f}",
                f"匹配帧: {self.recognition_stats['matched_frames']}",
                f"匹配率: {self._calculate_match_rate():.1f}%"
            ]
            
            if results.get('match_results'):
                best_match = results['match_results'][0]
                info_lines.extend([
                    f"商品: {best_match['template_name']}",
                    f"匹配点: {best_match['match_count']}",
                    f"置信度: {best_match['quality']:.2f}"
                ])
            
            y_offset = 30
            for line in info_lines:
                cv2.putText(display_frame, line, (10, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                y_offset += 20
            
            # 绘制识别区域
            cv2.rectangle(display_frame, (w//4, h//4), (3*w//4, 3*h//4), (0, 255, 0), 2)
        
        else:  # normal模式
            # 正常模式
            fps = self._calculate_fps()
            
            status_text = []
            if results.get('match_results'):
                best_match = results['match_results'][0]
                status_text.append(f"匹配: {best_match['template_name']} ({best_match['quality']:.2f})")
            else:
                status_text.append("未匹配到商品")
            
            status_text.append(f"帧: {self.recognition_stats['total_frames']}")
            status_text.append(f"FPS: {fps:.1f}")
            
            y_offset = 30
            for text in status_text:
                cv2.putText(display_frame, text, (10, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                y_offset += 25
        
        return display_frame
    
    def _calculate_fps(self):
        """计算当前FPS"""
        if not self.recognition_stats['start_time'] or self.recognition_stats['total_frames'] == 0:
            return 0
        
        elapsed = time.time() - self.recognition_stats['start_time']
        if elapsed > 0:
            return self.recognition_stats['total_frames'] / elapsed
        return 0
    
    def _calculate_match_rate(self):
        """计算匹配率"""
        if self.recognition_stats['total_frames'] == 0:
            return 0
        
        return (self.recognition_stats['matched_frames'] / 
                self.recognition_stats['total_frames'] * 100)
    
    def _save_current_frame(self, frame, results):
        """保存当前帧"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        # 如果有匹配结果，使用商品名作为文件名
        if results.get('match_results'):
            best_match = results['match_results'][0]
            product_name = best_match['template_name']
            filename = f"outputs/screen_matches/{product_name}_{timestamp}.jpg"
        else:
            filename = f"outputs/screen_matches/unknown_{timestamp}.jpg"
        
        # 确保目录存在
        Path("outputs/screen_matches").mkdir(parents=True, exist_ok=True)
        
        try:
            save_image(frame, filename)
            print(f"帧已保存: {filename}")
            self.output_mgr.log_system("_save_current_frame", f"保存帧: {filename}")
        except Exception as e:
            error_msg = f"保存帧失败: {e}"
            self.output_mgr.log_system("_save_current_frame", error_msg, "ERROR")
            print(error_msg)
    
    def _manual_learn_current(self, frame, results):
        """手动学习当前商品"""
        print("手动学习当前商品...")
        self.output_mgr.log_system("ScreenRecognition", "开始手动学习当前商品")
        
        # 提取ROI（如果可能）
        roi = None
        if results.get('match_results'):
            best_match = results['match_results'][0]
            if 'detection_bbox' in best_match:
                x, y, w, h = best_match['detection_bbox']
                roi = frame[y:y+h, x:x+w]
        
        # 学习ROI或整个帧
        learn_image = roi if roi is not None else frame
        
        # 输入商品名称
        item_name = input("请输入商品名称 (直接回车使用自动命名): ").strip()
        if not item_name:
            item_name = None
        
        success, item_info = self.learning_system.manual_learn(learn_image, item_name)
        
        if success:
            message = f"手动学习完成: {item_info['name']}"
            print(f"✅ {message}")
            self.output_mgr.log_system("_manual_learn_current", message)
        else:
            self.output_mgr.log_system("_manual_learn_current", "手动学习失败", "WARNING")
    
    def _cycle_display_mode(self, current_mode):
        """循环切换显示模式"""
        modes = ['normal', 'debug', 'minimal']
        current_index = modes.index(current_mode) if current_mode in modes else 0
        next_index = (current_index + 1) % len(modes)
        next_mode = modes[next_index]
        
        message = f"显示模式: {current_mode} -> {next_mode}"
        print(message)
        self.output_mgr.log_system("_cycle_display_mode", message)
        return next_mode
    
    def _show_recognition_stats(self):
        """显示识别统计"""
        if not self.recognition_stats['start_time']:
            return
        
        elapsed = time.time() - self.recognition_stats['start_time']
        
        print("\n" + "=" * 60)
        print("                    识别统计")
        print("=" * 60)
        print(f"识别时长: {elapsed:.1f}秒")
        print(f"总帧数: {self.recognition_stats['total_frames']}")
        print(f"匹配帧数: {self.recognition_stats['matched_frames']}")
        print(f"匹配率: {self._calculate_match_rate():.1f}%")
        print(f"平均FPS: {self._calculate_fps():.1f}")
        print(f"最后识别商品: {self.recognition_stats['current_product']}")
        print("=" * 60)
        
        # 记录统计信息到日志
        stats_message = (
            f"识别时长: {elapsed:.1f}秒, "
            f"总帧数: {self.recognition_stats['total_frames']}, "
            f"匹配帧数: {self.recognition_stats['matched_frames']}, "
            f"匹配率: {self._calculate_match_rate():.1f}%"
        )
        self.output_mgr.log_system("_show_recognition_stats", stats_message)
    
    def calibrate_screen(self):
        """校准屏幕区域"""
        print("\n[屏幕区域校准]")
        print("请按照提示选择要识别的屏幕区域")
        print("注意: 请确保要识别的视频窗口已经打开")
        
        # 记录校准开始
        self.output_mgr.log_system("ScreenRecognition", "开始屏幕区域校准")
        
        # 检查屏幕捕获器是否支持校准
        if not hasattr(self.screen_capture, 'calibrate_region'):
            print("❌ 当前屏幕捕获器不支持校准功能")
            self.output_mgr.log_system("ScreenRecognition", "屏幕捕获器不支持校准功能", "ERROR")
            return
        
        try:
            # 调用校准方法
            print("\n正在启动校准工具...")
            print("请用鼠标拖动选择要识别的区域，然后按回车确认")
            
            # 尝试校准
            if self.screen_capture.calibrate_region():
                # 获取校准后的区域
                region = self.screen_capture.region
                if region and len(region) >= 4:
                    print(f"✅ 屏幕区域校准成功!")
                    print(f"   区域: X={region[0]}, Y={region[1]}, 宽度={region[2]}, 高度={region[3]}")
                    print(f"   分辨率: {region[2]}x{region[3]}")
                    
                    # 记录校准成功日志
                    self.output_mgr.log_system("ScreenRecognition", 
                                             f"屏幕区域校准成功: {region}", "INFO")
                    
                    # 更新配置
                    if 'screen' not in self.config:
                        self.config['screen'] = {}
                    self.config['screen']['region'] = region
                    self._save_config()
                    
                    # 显示校准预览
                    print("\n正在捕获校准后的区域预览...")
                    preview = self.screen_capture.capture()
                    if preview is not None:
                        h, w = preview.shape[:2]
                        cv2.putText(preview, f"校准区域: {w}x{h}", 
                                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                                   0.7, (0, 255, 0), 2)
                        cv2.putText(preview, "按任意键关闭预览", 
                                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 
                                   0.5, (255, 255, 255), 1)
                        cv2.imshow('校准区域预览', preview)
                        cv2.waitKey(0)
                        cv2.destroyAllWindows()
                        
                        # 询问是否立即测试
                        choice = input("\n是否立即测试校准效果? (y/n): ").lower()
                        if choice == 'y':
                            self._test_calibrated_region()
                else:
                    print("❌ 校准失败: 未获取到有效的区域")
                    self.output_mgr.log_system("ScreenRecognition", "校准失败: 无效区域", "ERROR")
            else:
                print("❌ 校准失败: 用户取消或操作失败")
                self.output_mgr.log_system("ScreenRecognition", "校准失败: 用户取消", "INFO")
                
        except Exception as e:
            error_msg = f"校准过程中出现错误: {e}"
            print(f"❌ {error_msg}")
            self.output_mgr.log_system("ScreenRecognition", error_msg, "ERROR")
            import traceback
            traceback.print_exc()
    
    def _test_calibrated_region(self):
        """测试校准后的区域"""
        print("\n[测试校准区域]")
        print("正在测试校准的屏幕区域...")
        
        try:
            # 捕获校准区域
            frame = self.screen_capture.capture()
            if frame is None:
                print("❌ 无法捕获校准区域")
                return
            
            # 显示测试结果
            h, w = frame.shape[:2]
            print(f"✅ 校准区域测试成功!")
            print(f"   捕获尺寸: {w}x{h}")
            print(f"   帧类型: {type(frame)}")
            
            # 显示预览
            test_frame = frame.copy()
            cv2.putText(test_frame, f"测试区域: {w}x{h}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.7, (0, 255, 0), 2)
            cv2.putText(test_frame, "按任意键继续", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.5, (255, 255, 255), 1)
            cv2.imshow('校准区域测试', test_frame)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            
            # 询问是否识别测试
            choice = input("是否在测试区域中进行识别测试? (y/n): ").lower()
            if choice == 'y':
                self._quick_calibration_test(frame)
                
        except Exception as e:
            print(f"❌ 测试过程中出现错误: {e}")
    
    def _quick_calibration_test(self, frame):
        """快速校准测试"""
        print("\n[快速校准测试]")
        print("正在进行识别测试...")
        
        try:
            # 进行识别
            results = self.learning_system.process_frame(frame)
            
            if results.get('match_results'):
                best_match = results['match_results'][0]
                print(f"✅ 识别测试成功!")
                print(f"   识别到: {best_match['template_name']}")
                print(f"   置信度: {best_match['quality']:.2f}")
                
                # 记录测试结果
                self.output_mgr.log_screen_recognition(
                    best_match['template_name'],
                    best_match['quality'],
                    screen_region=str(self.screen_capture.region),
                    test_mode=True
                )
            else:
                print("ℹ️  未识别到已知商品")
                print("   可以添加模板或进行自动学习")
            
            # 显示测试帧
            display_frame = frame.copy()
            if results.get('match_results'):
                best_match = results['match_results'][0]
                cv2.putText(display_frame, f"识别: {best_match['template_name']}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                           0.7, (0, 255, 0), 2)
            else:
                cv2.putText(display_frame, "未识别到商品", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                           0.7, (0, 0, 255), 2)
            
            cv2.putText(display_frame, "按任意键继续", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.5, (255, 255, 255), 1)
            cv2.imshow('校准测试结果', display_frame)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            
        except Exception as e:
            print(f"❌ 识别测试过程中出现错误: {e}")
    
    def _load_templates(self):
        """加载模板"""
        template_dir = Path("data/images_material")
        if template_dir.exists():
            count = self.learning_system.image_matcher.load_templates_from_dir(template_dir)
            message = f"加载了 {count} 个模板"
            print(f"✓ {message}")
            self.output_mgr.log_system("_load_templates", message)
        else:
            error_msg = f"模板目录不存在: {template_dir}"
            print(error_msg)
            print("请将商品图片放入 data/images_material/")
            self.output_mgr.log_system("_load_templates", error_msg, "WARNING")
    
    def template_management(self):
        """模板管理"""
        print("\n[模板管理]")
        self.output_mgr.log_system("ScreenRecognition", "进入模板管理")
        
        while True:
            print("\n模板管理选项:")
            print("1. 查看当前模板")
            print("2. 添加模板图片")
            print("3. 从屏幕截图添加模板")
            print("4. 删除模板")
            print("5. 返回")
            
            choice = input("\n请选择 (1-5): ").strip()
            
            if choice == "1":
                self.show_templates()
            elif choice == "2":
                self.add_template_from_file()
            elif choice == "3":
                self.add_template_from_screen()
            elif choice == "4":
                self.delete_template()
            elif choice == "5":
                self.output_mgr.log_system("template_management", "退出模板管理")
                break
            else:
                print("无效选项")
                self.output_mgr.log_system("template_management", f"无效选项: {choice}", "WARNING")
    
    def show_templates(self):
        """显示当前模板"""
        templates = self.learning_system.image_matcher.templates
        
        print(f"\n当前模板 ({len(templates)} 个):")
        print("-" * 40)
        
        for i, (name, template) in enumerate(templates.items(), 1):
            print(f"{i:2}. {name:20} - 特征点: {len(template['keypoints'])}")
        
        print("-" * 40)
    
    def add_template_from_file(self):
        """从文件添加模板"""
        print("\n从文件添加模板...")
        self.output_mgr.log_system("add_template_from_file", "开始从文件添加模板")
        
        try:
            from utils.file_dialog import select_image_file
            image_path = select_image_file("选择模板图片")
            
            if image_path is None:
                print("未选择文件")
                return
            
            # 读取图像
            image = read_image(image_path)
            if image is None:
                error_msg = "无法读取图像文件"
                print(error_msg)
                self.output_mgr.log_system("add_template_from_file", error_msg, "ERROR")
                return
            
            # 输入模板名称
            default_name = image_path.stem
            item_name = input(f"请输入模板名称 (默认: {default_name}): ").strip()
            if not item_name:
                item_name = default_name
            
            # 添加到匹配器
            success = self.learning_system.image_matcher.add_template(item_name, image)
            
            if success:
                message = f"模板添加成功: {item_name}"
                print(f"✅ {message}")
                self.output_mgr.log_system("add_template_from_file", message)
                
                # 保存到模板目录
                template_dir = Path("data/images_material")
                template_dir.mkdir(exist_ok=True)
                save_path = template_dir / f"{item_name}.jpg"
                save_image(image, save_path)
                print(f"模板已保存: {save_path}")
            else:
                error_msg = "模板添加失败"
                print(f"❌ {error_msg}")
                self.output_mgr.log_system("add_template_from_file", error_msg, "ERROR")
                
        except Exception as e:
            error_msg = f"添加模板失败: {e}"
            print(error_msg)
            self.output_mgr.log_system("add_template_from_file", error_msg, "ERROR")
    
    def add_template_from_screen(self):
        """从屏幕截图添加模板"""
        print("\n从屏幕截图添加模板...")
        print("请准备好要识别的商品在屏幕上...")
        self.output_mgr.log_system("add_template_from_screen", "开始从屏幕截图添加模板")
        
        try:
            # 捕获一帧
            frame = self.screen_capture.capture()
            if frame is None:
                error_msg = "无法捕获屏幕"
                print(error_msg)
                self.output_mgr.log_system("add_template_from_screen", error_msg, "ERROR")
                return
            
            # 显示捕获的帧
            cv2.imshow("捕获的屏幕 - 按任意键继续", frame)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            
            # 让用户选择ROI
            print("请用鼠标选择商品区域...")
            roi = cv2.selectROI("选择商品区域", frame, False)
            cv2.destroyAllWindows()
            
            if roi[2] > 0 and roi[3] > 0:
                # 提取ROI
                x, y, w, h = map(int, roi)
                template_image = frame[y:y+h, x:x+w]
                
                # 显示ROI
                cv2.imshow("提取的商品", template_image)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
                
                # 输入模板名称
                item_name = input("请输入商品名称: ").strip()
                if not item_name:
                    print("商品名称不能为空")
                    return
                
                # 添加到匹配器
                success = self.learning_system.image_matcher.add_template(item_name, template_image)
                
                if success:
                    message = f"模板添加成功: {item_name}"
                    print(f"✅ {message}")
                    self.output_mgr.log_system("add_template_from_screen", message)
                    
                    # 保存到模板目录
                    template_dir = Path("data/images_material")
                    template_dir.mkdir(exist_ok=True)
                    save_path = template_dir / f"{item_name}.jpg"
                    save_image(template_image, save_path)
                    print(f"模板已保存: {save_path}")
                else:
                    error_msg = "模板添加失败"
                    print(f"❌ {error_msg}")
                    self.output_mgr.log_system("add_template_from_screen", error_msg, "ERROR")
            else:
                error_msg = "未选择有效区域"
                print(f"❌ {error_msg}")
                self.output_mgr.log_system("add_template_from_screen", error_msg, "WARNING")
        except Exception as e:
            error_msg = f"从屏幕截图添加模板失败: {e}"
            print(error_msg)
            self.output_mgr.log_system("add_template_from_screen", error_msg, "ERROR")
    
    def delete_template(self):
        """删除模板"""
        templates = self.learning_system.image_matcher.templates
        
        if not templates:
            print("没有模板可以删除")
            return
        
        print("\n选择要删除的模板:")
        
        template_list = list(templates.keys())
        for i, name in enumerate(template_list, 1):
            print(f"{i}. {name}")
        
        try:
            choice = int(input(f"\n请输入要删除的模板编号 (1-{len(template_list)}): "))
            if 1 <= choice <= len(template_list):
                template_name = template_list[choice - 1]
                
                confirm = input(f"确认删除模板 '{template_name}'? (y/n): ").lower()
                if confirm == 'y':
                    # 从匹配器中删除
                    del self.learning_system.image_matcher.templates[template_name]
                    
                    # 从文件系统中删除
                    template_file = Path(f"data/images_material/{template_name}.jpg")
                    if template_file.exists():
                        template_file.unlink()
                        print(f"模板文件已删除: {template_file}")
                    
                    message = f"模板已删除: {template_name}"
                    print(f"✅ {message}")
                    self.output_mgr.log_system("delete_template", message)
                else:
                    print("删除取消")
            else:
                print("无效的编号")
        except ValueError:
            error_msg = "无效的输入"
            print(error_msg)
            self.output_mgr.log_system("delete_template", error_msg, "WARNING")
    
    def recognition_settings(self):
        """识别设置"""
        print("\n[识别设置]")
        self.output_mgr.log_system("ScreenRecognition", "进入识别设置")
        
        while True:
            print("\n当前设置:")
            screen_config = self.config.get('screen', {})
            recog_config = self.config.get('recognition', {})
            
            print(f"1. 帧率: {screen_config.get('fps', 10)} FPS")
            print(f"2. 自动学习: {'启用' if recog_config.get('auto_learn', True) else '禁用'}")
            print(f"3. 最小置信度: {recog_config.get('min_confidence', 0.3)}")
            print(f"4. 匹配间隔: {recog_config.get('match_interval', 1)} 秒")
            print("5. 保存并应用")
            print("6. 取消")
            
            choice = input("\n请选择要修改的设置 (1-6): ").strip()
            
            if choice == "1":
                try:
                    fps = int(input("请输入帧率 (1-30): "))
                    if 1 <= fps <= 30:
                        self.config['screen']['fps'] = fps
                        message = f"帧率已设置为: {fps} FPS"
                        print(message)
                        self.output_mgr.log_system("recognition_settings", message)
                    else:
                        error_msg = "帧率必须在1-30之间"
                        print(error_msg)
                        self.output_mgr.log_system("recognition_settings", error_msg, "WARNING")
                except ValueError:
                    error_msg = "无效的输入"
                    print(error_msg)
                    self.output_mgr.log_system("recognition_settings", error_msg, "WARNING")
            
            elif choice == "2":
                current = self.config['recognition'].get('auto_learn', True)
                self.config['recognition']['auto_learn'] = not current
                message = f"自动学习已 {'启用' if not current else '禁用'}"
                print(message)
                self.output_mgr.log_system("recognition_settings", message)
            
            elif choice == "3":
                try:
                    confidence = float(input("请输入最小置信度 (0.1-0.9): "))
                    if 0.1 <= confidence <= 0.9:
                        self.config['recognition']['min_confidence'] = confidence
                        message = f"最小置信度已设置为: {confidence}"
                        print(message)
                        self.output_mgr.log_system("recognition_settings", message)
                    else:
                        error_msg = "置信度必须在0.1-0.9之间"
                        print(error_msg)
                        self.output_mgr.log_system("recognition_settings", error_msg, "WARNING")
                except ValueError:
                    error_msg = "无效的输入"
                    print(error_msg)
                    self.output_mgr.log_system("recognition_settings", error_msg, "WARNING")
            
            elif choice == "4":
                try:
                    interval = float(input("请输入匹配间隔(秒): "))
                    if interval > 0:
                        self.config['recognition']['match_interval'] = interval
                        message = f"匹配间隔已设置为: {interval} 秒"
                        print(message)
                        self.output_mgr.log_system("recognition_settings", message)
                    else:
                        error_msg = "间隔必须大于0"
                        print(error_msg)
                        self.output_mgr.log_system("recognition_settings", error_msg, "WARNING")
                except ValueError:
                    error_msg = "无效的输入"
                    print(error_msg)
                    self.output_mgr.log_system("recognition_settings", error_msg, "WARNING")
            
            elif choice == "5":
                # 保存配置
                self._save_config()
                message = "设置已保存并应用"
                print(f"✅ {message}")
                self.output_mgr.log_system("recognition_settings", message)
                break
            
            elif choice == "6":
                print("设置取消")
                self.output_mgr.log_system("recognition_settings", "设置取消")
                break
            
            else:
                print("无效选项")
                self.output_mgr.log_system("recognition_settings", f"无效选项: {choice}", "WARNING")
    
    def _save_config(self):
        """保存配置"""
        config_file = Path("config/screen_config.yaml")
        
        try:
            import yaml
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
            
            message = f"配置已保存: {config_file}"
            print(message)
            self.output_mgr.log_system("_save_config", message)
        except Exception as e:
            error_msg = f"保存配置失败: {e}"
            print(error_msg)
            self.output_mgr.log_system("_save_config", error_msg, "ERROR")
    
    def quick_test(self):
        """快速测试"""
        print("\n[快速测试]")
        print("这将进行5秒钟的快速识别测试...")
        self.output_mgr.log_system("ScreenRecognition", "开始快速测试")
        
        # 获取配置
        screen_config = self.config.get('screen', {})
        fps = screen_config.get('fps', 10)
        
        self.is_running = True
        start_time = time.time()
        frame_count = 0
        
        try:
            for frame in self.screen_capture.start_capture(fps=fps):
                if not self.is_running or frame is None:
                    break
                
                if time.time() - start_time >= 5:  # 5秒测试
                    break
                
                frame_count += 1
                
                # 每5帧进行一次识别
                if frame_count % 5 == 0:
                    results = self.learning_system.process_frame(frame)
                    
                    if results.get('match_results'):
                        best_match = results['match_results'][0]
                        message = (
                            f"帧 {frame_count}: 匹配到 {best_match['template_name']} "
                            f"(置信度: {best_match['quality']:.2f})"
                        )
                        print(message)
                        
                        # 记录到输出管理器
                        self.output_mgr.log_screen_recognition(
                            best_match['template_name'],
                            best_match['quality'],
                            screen_region=str(self.screen_capture.region),
                            test_mode=True
                        )
                
                # 显示测试画面
                test_frame = frame.copy()
                cv2.putText(test_frame, f"快速测试 - 帧: {frame_count}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                cv2.imshow('快速测试', test_frame)
                cv2.waitKey(1)
        
        except Exception as e:
            error_msg = f"快速测试出错: {e}"
            print(error_msg)
            self.output_mgr.log_system("quick_test", error_msg, "ERROR")
        finally:
            self.is_running = False
            self.screen_capture.stop_capture()
            cv2.destroyAllWindows()
            
            message = f"测试完成，共处理 {frame_count} 帧，平均帧率: {frame_count/5:.1f} FPS"
            print(f"\n{message}")
            self.output_mgr.log_system("quick_test", message)

# 主函数
def main():
    """主函数"""
    # 创建必要的目录
    os.makedirs("data/images_material", exist_ok=True)
    os.makedirs("outputs/screen_matches", exist_ok=True)
    os.makedirs("config", exist_ok=True)
    
    # 创建屏幕识别系统
    system = ScreenRecognitionSystem()
    
    # 运行系统
    system.run()

if __name__ == "__main__":
    main()
    input("\n按Enter键退出程序...")
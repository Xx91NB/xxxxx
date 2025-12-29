#!/usr/bin/env python3
"""
智能系统核心
整合所有组件，提供完整的商品识别流程
"""
import cv2
import numpy as np
import time
import json
from pathlib import Path
from datetime import datetime
import yaml

class IntelligentSystem:
    def __init__(self, config_path="config/default.yaml"):
        """
        初始化智能系统
        
        参数:
            config_path: 配置文件路径
        """
        print("=" * 50)
        print("      直播商品识别系统 - 智能核心")
        print("=" * 50)
        
        # 加载配置
        self.config = self._load_config(config_path)
        print("✓ 配置加载完成")
        
        # 初始化组件
        self._init_components()
        
        # 状态变量
        self.is_running = False
        self.processing_stats = {
            'frames_processed': 0,
            'products_detected': 0,
            'matches_found': 0,
            'start_time': None,
            'current_product': None
        }
        
        # 学习数据
        self.learned_products = {}
        self._load_learned_data()
        
        print("智能系统初始化完成")
        print(f"模式: {self.config.get('system', {}).get('default_mode', 'hybrid')}")
    
    def _load_config(self, config_path):
        """加载配置文件"""
        config_file = Path(config_path)
        
        if not config_file.exists():
            print(f"警告: 配置文件不存在 {config_file}，使用默认配置")
            return self._get_default_config()
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            print(f"加载配置失败: {e}，使用默认配置")
            return self._get_default_config()
    
    def _get_default_config(self):
        """获取默认配置"""
        return {
            'system': {
                'default_mode': 'hybrid',
                'auto_save_interval': 300,
                'max_log_files': 10
            },
            'detector': {
                'confidence_threshold': 0.5
            },
            'matcher': {
                'image': {
                    'feature_type': 'orb',
                    'min_matches': 10
                },
                'video': {
                    'frame_interval': 1,
                    'min_confidence': 0.3
                }
            },
            'paths': {
                'data': './data',
                'outputs': './outputs',
                'config': './config'
            }
        }
    
    def _init_components(self):
        """初始化所有组件"""
        # 导入组件
        try:
            from detector import ProductDetector
            from advanced_matcher import AdvancedMatcher
            
            # 初始化检测器
            detector_config = self.config.get('detector', {})
            self.detector = ProductDetector(detector_config)
            
            # 初始化高级匹配器
            matcher_config = self.config.get('matcher', {})
            matcher_config['mode'] = self.config.get('system', {}).get('default_mode', 'hybrid')
            self.matcher = AdvancedMatcher(matcher_config)
            
            print("✓ 组件初始化完成")
            
        except ImportError as e:
            print(f"导入组件失败: {e}")
            raise
    
    def _load_learned_data(self):
        """加载学习数据"""
        learned_file = Path("data/learned_samples/learned_products.json")
        if learned_file.exists():
            try:
                with open(learned_file, 'r', encoding='utf-8') as f:
                    self.learned_products = json.load(f)
                print(f"✓ 加载了 {len(self.learned_products)} 个学习样本")
            except Exception as e:
                print(f"加载学习数据失败: {e}")
    
    def _save_learned_data(self):
        """保存学习数据"""
        learned_dir = Path("data/learned_samples")
        learned_dir.mkdir(parents=True, exist_ok=True)
        
        learned_file = learned_dir / "learned_products.json"
        try:
            with open(learned_file, 'w', encoding='utf-8') as f:
                json.dump(self.learned_products, f, indent=2, ensure_ascii=False)
            print(f"学习数据已保存: {learned_file}")
        except Exception as e:
            print(f"保存学习数据失败: {e}")
    
    def run_with_gui(self, input_source=0):
        """
        运行带GUI的系统
        
        参数:
            input_source: 输入源（摄像头ID或视频文件路径）
        """
        print(f"启动GUI模式，输入源: {input_source}")
        
        # 打开输入源
        if isinstance(input_source, str) and input_source.isdigit():
            input_source = int(input_source)
        
        cap = self._open_input_source(input_source)
        if not cap:
            print("无法打开输入源")
            return
        
        # 加载模板
        self._load_templates()
        
        # 初始化状态
        self.is_running = True
        self.processing_stats['start_time'] = time.time()
        
        print("系统运行中...")
        print("快捷键:")
        print("  q - 退出")
        print("  s - 保存截图")
        print("  l - 学习当前商品")
        print("  1 - 切换到图像模式")
        print("  2 - 切换到视频模式")
        print("  3 - 切换到混合模式")
        print()
        
        try:
            while self.is_running:
                # 读取帧
                ret, frame = cap.read()
                if not ret:
                    print("无法读取帧")
                    break
                
                # 处理帧
                results = self._process_frame(frame)
                
                # 更新统计数据
                self.processing_stats['frames_processed'] += 1
                if results.get('matches'):
                    self.processing_stats['matches_found'] += 1
                
                # 绘制结果
                annotated_frame = self._draw_results(frame, results)
                
                # 显示帧
                cv2.imshow('直播商品识别系统', annotated_frame)
                
                # 处理按键
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    self._save_screenshot(annotated_frame)
                elif key == ord('l'):
                    self._learn_current_product(frame, results)
                elif key == ord('1'):
                    self.matcher.switch_mode('image')
                elif key == ord('2'):
                    self.matcher.switch_mode('video')
                elif key == ord('3'):
                    self.matcher.switch_mode('hybrid')
                
                # 自动保存检查
                self._check_auto_save()
        
        except KeyboardInterrupt:
            print("\n用户中断")
        except Exception as e:
            print(f"运行出错: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # 清理
            self.is_running = False
            cap.release()
            cv2.destroyAllWindows()
            
            # 保存学习数据
            self._save_learned_data()
            
            # 打印统计信息
            self._print_statistics()
    
    def run_headless(self, input_source, output_dir="outputs"):
        """
        无GUI运行系统
        
        参数:
            input_source: 输入源
            output_dir: 输出目录
        """
        print(f"启动无GUI模式，输入源: {input_source}")
        
        # 打开输入源
        cap = self._open_input_source(input_source)
        if not cap:
            print("无法打开输入源")
            return
        
        # 加载模板
        self._load_templates()
        
        # 准备输出
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 初始化状态
        self.is_running = True
        self.processing_stats['start_time'] = time.time()
        
        print("开始处理...")
        
        try:
            frame_count = 0
            
            while self.is_running:
                # 读取帧
                ret, frame = cap.read()
                if not ret:
                    print("无法读取帧，可能已结束")
                    break
                
                frame_count += 1
                
                # 处理帧
                results = self._process_frame(frame)
                
                # 更新统计数据
                self.processing_stats['frames_processed'] += 1
                if results.get('matches'):
                    self.processing_stats['matches_found'] += 1
                
                # 显示进度
                if frame_count % 100 == 0:
                    elapsed = time.time() - self.processing_stats['start_time']
                    fps = frame_count / elapsed if elapsed > 0 else 0
                    print(f"已处理 {frame_count} 帧, FPS: {fps:.1f}")
                
                # 自动保存检查
                self._check_auto_save()
        
        except KeyboardInterrupt:
            print("\n用户中断")
        except Exception as e:
            print(f"运行出错: {e}")
        finally:
            # 清理
            self.is_running = False
            cap.release()
            
            # 保存学习数据
            self._save_learned_data()
            
            # 打印统计信息
            self._print_statistics()
    
    def _open_input_source(self, source):
        """打开输入源"""
        if source == "screen":
            # 屏幕捕获（需要安装额外的库）
            print("屏幕捕获模式暂不支持")
            return None
        elif isinstance(source, str) and Path(source).exists():
            # 视频文件
            cap = cv2.VideoCapture(source)
            if not cap.isOpened():
                print(f"无法打开视频文件: {source}")
                return None
            print(f"打开视频文件: {source}")
            return cap
        else:
            # 摄像头
            if isinstance(source, str) and source.isdigit():
                source = int(source)
            cap = cv2.VideoCapture(source)
            if not cap.isOpened():
                print(f"无法打开摄像头: {source}")
                return None
            print(f"打开摄像头: {source}")
            return cap
    
    def _load_templates(self):
        """加载模板"""
        # 图像模板
        image_dir = Path(self.config.get('paths', {}).get('materials', {}).get('images', 'data/images_material'))
        if image_dir.exists():
            count = self.matcher.load_templates(str(image_dir))
            print(f"加载了 {count} 个图像模板")
        else:
            print(f"图像模板目录不存在: {image_dir}")
        
        # 视频模板（如果需要）
        video_dir = Path(self.config.get('paths', {}).get('materials', {}).get('videos', 'data/videos_material'))
        if video_dir.exists() and self.matcher.mode == 'video':
            self.matcher.load_templates(video_dir=str(video_dir))
    
    def _process_frame(self, frame):
        """处理单帧"""
        try:
            # 使用匹配器处理
            results = self.matcher.process(frame)
            
            # 如果有匹配结果，更新当前商品
            if results.get('matches'):
                best_match = results['matches'][0] if results['matches'] else None
                if best_match:
                    product_name = best_match.get('template_name', 'Unknown')
                    self.processing_stats['current_product'] = product_name
                    
                    # 记录到学习数据
                    if product_name not in self.learned_products:
                        self.learned_products[product_name] = {
                            'first_seen': time.time(),
                            'last_seen': time.time(),
                            'count': 1
                        }
                    else:
                        self.learned_products[product_name]['last_seen'] = time.time()
                        self.learned_products[product_name]['count'] += 1
            
            return results
            
        except Exception as e:
            print(f"处理帧时出错: {e}")
            return {'error': str(e), 'success': False}
    
    def _draw_results(self, frame, results):
        """绘制结果"""
        # 使用匹配器绘制基本结果
        annotated_frame = self.matcher.draw_results(frame, results)
        
        # 添加系统信息
        fps = self._calculate_fps()
        
        # 系统状态文本
        status_lines = [
            f"FPS: {fps:.1f}",
            f"Frames: {self.processing_stats['frames_processed']}",
            f"Matches: {self.processing_stats['matches_found']}",
            f"Product: {self.processing_stats['current_product'] or 'None'}"
        ]
        
        # 绘制状态文本
        y_offset = annotated_frame.shape[0] - 100
        for line in status_lines:
            cv2.putText(annotated_frame, line, (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            y_offset += 20
        
        return annotated_frame
    
    def _calculate_fps(self):
        """计算当前FPS"""
        if not self.processing_stats['start_time'] or self.processing_stats['frames_processed'] == 0:
            return 0
        
        elapsed = time.time() - self.processing_stats['start_time']
        if elapsed > 0:
            return self.processing_stats['frames_processed'] / elapsed
        return 0
    
    def _save_screenshot(self, frame):
        """保存截图"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"outputs/screenshots/screenshot_{timestamp}.jpg"
        
        # 确保目录存在
        Path("outputs/screenshots").mkdir(parents=True, exist_ok=True)
        
        cv2.imwrite(filename, frame)
        print(f"截图已保存: {filename}")
    
    def _learn_current_product(self, frame, results):
        """学习当前商品"""
        if not results.get('matches'):
            print("没有匹配结果可供学习")
            return
        
        best_match = results['matches'][0]
        product_name = best_match.get('template_name', 'Unknown')
        
        # 保存学习样本
        samples_dir = Path("data/learned_samples/images")
        samples_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = samples_dir / f"{product_name}_{timestamp}.jpg"
        
        cv2.imwrite(str(filename), frame)
        
        print(f"学习样本已保存: {filename}")
    
    def _check_auto_save(self):
        """检查自动保存"""
        auto_save_interval = self.config.get('system', {}).get('auto_save_interval', 300)
        
        if auto_save_interval > 0:
            current_time = time.time()
            last_save = getattr(self, '_last_save_time', 0)
            
            if current_time - last_save > auto_save_interval:
                self._save_learned_data()
                self._last_save_time = current_time
    
    def _print_statistics(self):
        """打印统计信息"""
        if not self.processing_stats['start_time']:
            return
        
        elapsed = time.time() - self.processing_stats['start_time']
        
        print("\n" + "=" * 50)
        print("处理统计")
        print("=" * 50)
        print(f"总处理时间: {elapsed:.1f}秒")
        print(f"处理帧数: {self.processing_stats['frames_processed']}")
        print(f"平均FPS: {self.processing_stats['frames_processed']/elapsed:.1f}")
        print(f"匹配次数: {self.processing_stats['matches_found']}")
        print(f"匹配率: {self.processing_stats['matches_found']/self.processing_stats['frames_processed']*100:.1f}%")
        print(f"学习样本数: {len(self.learned_products)}")
        print("=" * 50)

# 主函数
if __name__ == "__main__":
    # 创建系统
    system = IntelligentSystem("config/default.yaml")
    
    # 运行GUI模式
    system.run_with_gui(0)
#!/usr/bin/env python3
"""
自动学习模块
当系统遇到未知商品时自动学习
"""
import cv2
import numpy as np
import time
import json
from pathlib import Path
from datetime import datetime
from image_matcher import ImageMatcher

class AutoLearner:
    def __init__(self, config=None):
        """初始化自动学习器"""
        self.config = config or {}
        
        # 学习参数
        self.learning_enabled = self.config.get('learning_enabled', True)
        self.min_confidence = self.config.get('min_confidence', 0.3)
        self.learning_threshold = self.config.get('learning_threshold', 0.2)
        self.max_learned_items = self.config.get('max_learned_items', 100)
        
        # 路径设置
        self.learned_dir = Path("data/learned_samples")
        self.learned_dir.mkdir(parents=True, exist_ok=True)
        
        # 学习数据
        self.learned_items = []
        self.learning_history = []
        
        # 加载已有学习数据
        self._load_learning_data()
        
        print(f"自动学习器初始化，已学习 {len(self.learned_items)} 个商品")
    
    def _load_learning_data(self):
        """加载学习数据"""
        data_file = self.learned_dir / "learning_data.json"
        
        if data_file.exists():
            try:
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.learned_items = data.get('learned_items', [])
                    self.learning_history = data.get('learning_history', [])
                print(f"✓ 加载了 {len(self.learned_items)} 个学习记录")
            except Exception as e:
                print(f"加载学习数据失败: {e}")
    
    def _save_learning_data(self):
        """保存学习数据"""
        data_file = self.learned_dir / "learning_data.json"
        
        data = {
            'learned_items': self.learned_items,
            'learning_history': self.learning_history,
            'last_updated': datetime.now().isoformat(),
            'total_learned': len(self.learned_items)
        }
        
        try:
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"学习数据已保存: {data_file}")
        except Exception as e:
            print(f"保存学习数据失败: {e}")
    
    def should_learn(self, match_results, frame):
        """
        判断是否应该学习当前商品
        
        参数:
            match_results: 匹配结果
            frame: 当前帧
            
        返回:
            should_learn: 是否应该学习
            reason: 学习原因
        """
        if not self.learning_enabled:
            return False, "学习功能已禁用"
        
        # 如果匹配结果为空，说明是完全未知的商品
        if not match_results:
            return True, "完全未知的商品"
        
        # 获取最佳匹配的置信度
        best_match = match_results[0]
        confidence = best_match.get('quality', 0)
        
        # 如果置信度低于阈值，说明匹配度不够，可能是新商品或变种
        if confidence < self.learning_threshold:
            return True, f"匹配置信度过低 ({confidence:.2f} < {self.learning_threshold})"
        
        return False, "不需要学习"
    
    def learn_new_item(self, frame, item_name=None, context=None):
        """
        学习新商品
        
        参数:
            frame: 商品图像
            item_name: 商品名称（自动生成）
            context: 学习上下文信息
            
        返回:
            success: 是否成功
            item_info: 商品信息
        """
        try:
            # 生成商品名称
            if item_name is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                item_name = f"learned_item_{timestamp}"
            
            # 保存商品图像
            image_dir = self.learned_dir / "images"
            image_dir.mkdir(exist_ok=True)
            
            image_path = image_dir / f"{item_name}.jpg"
            cv2.imwrite(str(image_path), frame)
            
            # 创建商品信息
            item_info = {
                'name': item_name,
                'image_path': str(image_path),
                'learned_at': datetime.now().isoformat(),
                'context': context or {},
                'image_shape': frame.shape,
                'confidence': 0.0  # 初始置信度
            }
            
            # 添加到学习列表
            self.learned_items.append(item_info)
            
            # 记录学习历史
            history_entry = {
                'timestamp': datetime.now().isoformat(),
                'item_name': item_name,
                'action': 'learn',
                'context': context or {}
            }
            self.learning_history.append(history_entry)
            
            # 保存数据
            self._save_learning_data()
            
            # 如果超过最大数量，移除最旧的
            if len(self.learned_items) > self.max_learned_items:
                removed = self.learned_items.pop(0)
                print(f"移除最旧的学习项: {removed['name']}")
            
            print(f"✅ 已学习新商品: {item_name}")
            return True, item_info
            
        except Exception as e:
            print(f"学习商品失败: {e}")
            return False, None
    
    def auto_learn_from_frame(self, frame, match_results):
        """
        从当前帧自动学习
        
        参数:
            frame: 当前帧
            match_results: 匹配结果
            
        返回:
            learned: 是否学习了新商品
            item_info: 学习到的商品信息
        """
        should_learn, reason = self.should_learn(match_results, frame)
        
        if should_learn:
            print(f"🤖 自动学习触发: {reason}")
            
            # 提取ROI（如果可能）
            roi = self._extract_roi(frame, match_results)
            
            # 学习ROI或整个帧
            learn_image = roi if roi is not None else frame
            
            # 生成有意义的名称
            item_name = self._generate_item_name(match_results)
            
            # 学习新商品
            context = {
                'reason': reason,
                'match_results': match_results,
                'auto_learned': True
            }
            
            success, item_info = self.learn_new_item(learn_image, item_name, context)
            
            if success:
                print(f"🎯 自动学习完成: {item_info['name']}")
                return True, item_info
        
        return False, None
    
    def _extract_roi(self, frame, match_results):
        """从帧中提取ROI（感兴趣区域）"""
        try:
            # 如果有匹配结果，尝试使用匹配的区域
            if match_results:
                best_match = match_results[0]
                if 'detection_bbox' in best_match:
                    x, y, w, h = best_match['detection_bbox']
                    roi = frame[y:y+h, x:x+w]
                    if roi.size > 0:
                        return roi
            
            # 如果没有检测框，使用图像中心区域
            h, w = frame.shape[:2]
            center_x, center_y = w // 2, h // 2
            roi_size = min(w, h) // 2
            
            x1 = max(0, center_x - roi_size // 2)
            y1 = max(0, center_y - roi_size // 2)
            x2 = min(w, center_x + roi_size // 2)
            y2 = min(h, center_y + roi_size // 2)
            
            roi = frame[y1:y2, x1:x2]
            if roi.size > 0:
                return roi
            
            return None
            
        except Exception as e:
            print(f"提取ROI失败: {e}")
            return None
    
    def _generate_item_name(self, match_results):
        """生成商品名称"""
        timestamp = datetime.now().strftime("%m%d_%H%M")
        
        # 如果有匹配结果，基于匹配结果命名
        if match_results:
            best_match = match_results[0]
            base_name = best_match.get('template_name', 'unknown')
            
            # 如果有置信度信息
            confidence = best_match.get('quality', 0)
            if confidence > 0.1:
                conf_str = f"_{int(confidence*100)}"
                return f"{base_name}_variant{conf_str}_{timestamp}"
            else:
                return f"new_{base_name}_{timestamp}"
        else:
            # 完全未知的商品
            return f"unknown_item_{timestamp}"
    
    def get_learning_stats(self):
        """获取学习统计信息"""
        return {
            'total_learned': len(self.learned_items),
            'learning_history_count': len(self.learning_history),
            'last_learned': self.learned_items[-1]['name'] if self.learned_items else None,
            'learning_enabled': self.learning_enabled
        }
    
    def merge_with_templates(self, template_dir):
        """
        将学习到的商品合并到模板库
        
        参数:
            template_dir: 模板目录路径
            
        返回:
            merged_count: 合并的数量
        """
        template_dir = Path(template_dir)
        template_dir.mkdir(exist_ok=True)
        
        merged_count = 0
        
        for item in self.learned_items:
            try:
                # 检查是否已经存在
                image_path = Path(item['image_path'])
                if not image_path.exists():
                    continue
                
                # 目标路径
                target_path = template_dir / f"{item['name']}.jpg"
                
                # 如果不存在，则复制
                if not target_path.exists():
                    import shutil
                    shutil.copy2(image_path, target_path)
                    merged_count += 1
                    print(f"合并模板: {item['name']}")
                    
            except Exception as e:
                print(f"合并模板失败 {item['name']}: {e}")
        
        print(f"共合并 {merged_count} 个学习商品到模板库")
        return merged_count

# 创建智能学习系统
class SmartLearningSystem:
    def __init__(self):
        """初始化智能学习系统"""
        print("🤖 初始化智能学习系统...")
        
        # 初始化自动学习器
        self.auto_learner = AutoLearner({
            'learning_enabled': True,
            'min_confidence': 0.25,
            'learning_threshold': 0.35,
            'max_learned_items': 50
        })
        
        # 初始化图像匹配器
        self.image_matcher = ImageMatcher()
        
        # 加载模板
        self.template_dir = Path("data/images_material")
        self.template_dir.mkdir(parents=True, exist_ok=True)
        self.image_matcher.load_templates_from_dir(self.template_dir)
        
        # 学习统计
        self.learning_stats = {
            'auto_learned_count': 0,
            'manual_learned_count': 0,
            'total_processed_frames': 0,
            'last_learned_item': None
        }
        
        print("✅ 智能学习系统初始化完成")
    
    def process_frame(self, frame):
        """
        处理一帧图像
        
        参数:
            frame: 输入帧
            
        返回:
            results: 处理结果
        """
        self.learning_stats['total_processed_frames'] += 1
        
        try:
            # 1. 进行图像匹配
            match_results = self.image_matcher.match(frame)
            
            # 2. 自动学习判断
            learned, learned_item = self.auto_learner.auto_learn_from_frame(frame, match_results)
            
            if learned:
                self.learning_stats['auto_learned_count'] += 1
                self.learning_stats['last_learned_item'] = learned_item['name']
                
                # 3. 如果学习了新商品，重新加载模板
                self.image_matcher.load_templates_from_dir(self.template_dir)
                print(f"🔄 模板库已更新，当前模板数: {len(self.image_matcher.templates)}")
            
            return {
                'match_results': match_results,
                'learned': learned,
                'learned_item': learned_item,
                'stats': self.learning_stats.copy()
            }
            
        except Exception as e:
            print(f"处理帧失败: {e}")
            return {
                'error': str(e),
                'match_results': [],
                'learned': False,
                'stats': self.learning_stats.copy()
            }
    
    def manual_learn(self, frame, item_name=None):
        """
        手动学习新商品
        
        参数:
            frame: 商品图像
            item_name: 商品名称
        """
        success, item_info = self.auto_learner.learn_new_item(frame, item_name, {
            'manual_learn': True,
            'source': 'user'
        })
        
        if success:
            self.learning_stats['manual_learned_count'] += 1
            self.learning_stats['last_learned_item'] = item_info['name']
            
            # 重新加载模板
            self.image_matcher.load_templates_from_dir(self.template_dir)
            
            print(f"📝 手动学习完成: {item_info['name']}")
        
        return success, item_info
    
    def get_learning_summary(self):
        """获取学习摘要"""
        learner_stats = self.auto_learner.get_learning_stats()
        
        return {
            **self.learning_stats,
            **learner_stats,
            'current_templates': len(self.image_matcher.templates),
            'template_dir': str(self.template_dir)
        }
    
    def run_auto_learning_demo(self, duration_seconds=30):
        """
        运行自动学习演示
        
        参数:
            duration_seconds: 演示时长（秒）
        """
        print(f"🚀 启动自动学习演示 ({duration_seconds}秒)...")
        print("请向摄像头展示不同的商品")
        print("系统会自动学习未知商品")
        print("按 'q' 提前退出")
        
        import cv2
        import time
        
        # 打开摄像头
        for camera_id in [0, 1, 2]:
            cap = cv2.VideoCapture(camera_id)
            if cap.isOpened():
                print(f"✓ 打开摄像头 {camera_id}")
                break
            cap.release()
        else:
            print("无法打开摄像头")
            return
        
        start_time = time.time()
        frame_count = 0
        learned_count = 0
        
        while time.time() - start_time < duration_seconds:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # 处理帧
            results = self.process_frame(frame)
            
            # 显示结果
            display_frame = frame.copy()
            h, w = display_frame.shape[:2]
            
            # 显示状态信息
            status_text = []
            
            if results.get('match_results'):
                best_match = results['match_results'][0]
                status_text.append(f"匹配: {best_match['template_name']}")
                status_text.append(f"置信度: {best_match['quality']:.2f}")
            else:
                status_text.append("未知商品")
            
            if results.get('learned'):
                status_text.append("🎯 正在学习...")
                learned_count += 1
            
            status_text.append(f"帧: {frame_count}")
            status_text.append(f"已学习: {learned_count}")
            
            # 绘制状态信息
            y_offset = 30
            for text in status_text:
                cv2.putText(display_frame, text, (10, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                y_offset += 25
            
            # 绘制学习区域
            cv2.rectangle(display_frame, 
                         (w//4, h//4), 
                         (3*w//4, 3*h//4), 
                         (0, 255, 0), 2)
            
            cv2.imshow("自动学习演示", display_frame)
            
            # 按键处理
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # 清理
        cap.release()
        cv2.destroyAllWindows()
        
        # 打印学习摘要
        self._print_learning_summary()
        
        print(f"演示结束，共处理 {frame_count} 帧，自动学习了 {learned_count} 个商品")
    
    def _print_learning_summary(self):
        """打印学习摘要"""
        summary = self.get_learning_summary()
        
        print("\n" + "=" * 60)
        print("                    学习摘要")
        print("=" * 60)
        print(f"总处理帧数: {summary['total_processed_frames']}")
        print(f"自动学习次数: {summary['auto_learned_count']}")
        print(f"手动学习次数: {summary['manual_learned_count']}")
        print(f"总学习商品数: {summary['total_learned']}")
        print(f"当前模板数: {summary['current_templates']}")
        print(f"最后学习商品: {summary['last_learned_item']}")
        print(f"学习功能: {'启用' if summary['learning_enabled'] else '禁用'}")
        print("=" * 60)

# 演示函数
def demo_auto_learning():
    """演示自动学习功能"""
    print("🤖 直播商品识别系统 - 自动学习演示")
    print("=" * 60)
    
    # 创建智能学习系统
    system = SmartLearningSystem()
    
    # 显示当前状态
    summary = system.get_learning_summary()
    print(f"当前模板数: {summary['current_templates']}")
    print(f"已学习商品数: {summary['total_learned']}")
    print()
    
    # 运行自动学习演示
    try:
        system.run_auto_learning_demo(duration_seconds=30)
    except KeyboardInterrupt:
        print("\n演示被用户中断")
    
    # 保存学习数据
    system.auto_learner._save_learning_data()
    
    # 询问是否合并学习到的商品到模板库
    choice = input("\n是否将学习到的商品合并到模板库? (y/n): ").lower()
    if choice == 'y':
        merged = system.auto_learner.merge_with_templates("data/images_material")
        print(f"已合并 {merged} 个商品到模板库")

if __name__ == "__main__":
    demo_auto_learning()
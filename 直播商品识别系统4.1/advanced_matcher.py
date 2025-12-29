#!/usr/bin/env python3
"""
高级匹配器模块
整合多种匹配方法，实现智能匹配策略
"""
import cv2
import numpy as np
import time
from pathlib import Path
from detector import ProductDetector
from image_matcher import ImageMatcher
from video_matcher import VideoMatcher

class AdvancedMatcher:
    def __init__(self, config=None):
        """
        初始化高级匹配器
        
        参数:
            config: 配置字典
        """
        self.config = config or {}
        
        # 模式配置
        self.mode = self.config.get('mode', 'hybrid')  # hybrid, image, video
        self.primary_method = self.config.get('primary_method', 'image')
        self.fallback_to_video = self.config.get('fallback_to_video', True)
        
        # 初始化各个组件
        print("初始化高级匹配器...")
        
        # 商品检测器
        detector_config = self.config.get('detector', {})
        self.detector = ProductDetector(detector_config)
        print("✓ 商品检测器初始化完成")
        
        # 图像匹配器
        image_config = self.config.get('image_matcher', {})
        self.image_matcher = ImageMatcher(image_config)
        print("✓ 图像匹配器初始化完成")
        
        # 视频匹配器
        video_config = self.config.get('video_matcher', {})
        self.video_matcher = VideoMatcher(video_config)
        print("✓ 视频匹配器初始化完成")
        
        # 状态变量
        self.last_match_time = 0
        self.match_history = []
        self.max_history_size = 100
        
        print("高级匹配器初始化完成")
    
    def load_templates(self, image_dir=None, video_dir=None):
        """
        加载模板
        
        参数:
            image_dir: 图像模板目录
            video_dir: 视频模板目录
            
        返回:
            加载的模板总数
        """
        count = 0
        
        # 加载图像模板
        if image_dir:
            image_count = self.image_matcher.load_templates_from_dir(image_dir)
            count += image_count
            print(f"加载了 {image_count} 个图像模板")
        
        # 加载视频模板（如果需要）
        if video_dir and Path(video_dir).exists():
            video_count = self.video_matcher.load_templates(video_dir)
            count += video_count
            print(f"加载了 {video_count} 个视频模板")
        
        return count
    
    def process(self, frame, mode=None):
        """
        处理帧
        
        参数:
            frame: 输入帧
            mode: 处理模式（覆盖配置）
            
        返回:
            results: 处理结果
        """
        current_mode = mode or self.mode
        current_time = time.time()
        
        if current_mode == 'image':
            results = self._process_image_mode(frame)
        elif current_mode == 'video':
            results = self._process_video_mode(frame)
        elif current_mode == 'hybrid':
            results = self._process_hybrid_mode(frame)
        else:
            results = {'error': f'未知模式: {current_mode}'}
        
        # 记录匹配历史
        if results.get('success', False):
            history_entry = {
                'timestamp': current_time,
                'mode': current_mode,
                'matches': results.get('matches', []),
                'detections': results.get('detections', [])
            }
            self.match_history.append(history_entry)
            
            # 限制历史记录大小
            if len(self.match_history) > self.max_history_size:
                self.match_history = self.match_history[-self.max_history_size:]
        
        return results
    
    def _process_image_mode(self, frame):
        """图像模式处理"""
        # 先检测商品区域
        detections = self.detector.detect(frame)
        
        results = {
            'mode': 'image',
            'detections': detections,
            'matches': [],
            'success': False
        }
        
        # 如果没有检测到商品，对整个图像进行匹配
        if not detections:
            matches = self.image_matcher.match(frame)
            if matches:
                results['matches'] = matches
                results['success'] = True
            return results
        
        # 对每个检测到的区域进行匹配
        for detection in detections:
            x, y, w, h = detection['bbox']
            
            # 提取ROI
            roi = frame[y:y+h, x:x+w]
            if roi.size == 0:
                continue
            
            # 匹配ROI
            matches = self.image_matcher.match(roi)
            
            # 将匹配结果转换为全局坐标
            for match in matches:
                # 添加检测框信息
                match['detection_bbox'] = [x, y, w, h]
                
                # 调整关键点坐标（如果需要）
                if match['keypoints']:
                    for kp in match['keypoints']:
                        kp.pt = (kp.pt[0] + x, kp.pt[1] + y)
            
            results['matches'].extend(matches)
        
        if results['matches']:
            results['success'] = True
        
        return results
    
    def _process_video_mode(self, frame):
        """视频模式处理"""
        results = self.video_matcher.process_frame(frame)
        results['mode'] = 'video'
        results['success'] = len(results['matches']) > 0
        
        return results
    
    def _process_hybrid_mode(self, frame):
        """混合模式处理"""
        # 先用主方法（图像匹配）
        primary_results = self._process_image_mode(frame)
        
        # 如果主方法失败且启用了备用方法，尝试视频匹配
        if not primary_results['success'] and self.fallback_to_video:
            secondary_results = self._process_video_mode(frame)
            
            # 如果备用方法成功，使用备用结果
            if secondary_results['success']:
                primary_results = secondary_results
                primary_results['mode'] = 'hybrid_fallback'
            else:
                primary_results['mode'] = 'hybrid_primary'
        else:
            primary_results['mode'] = 'hybrid_primary'
        
        return primary_results
    
    def draw_results(self, frame, results):
        """
        绘制处理结果
        
        参数:
            frame: 原始帧
            results: 处理结果
            
        返回:
            annotated_frame: 标注后的帧
        """
        annotated_frame = frame.copy()
        
        # 绘制检测框
        for detection in results.get('detections', []):
            x, y, w, h = detection['bbox']
            cv2.rectangle(annotated_frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
            # 绘制标签
            label = detection.get('label', 'Object')
            confidence = detection.get('confidence', 0.0)
            text = f"{label}: {confidence:.2f}"
            cv2.putText(annotated_frame, text, (x, y-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        
        # 绘制匹配结果
        y_offset = 30
        for i, match in enumerate(results.get('matches', [])):
            if i >= 5:  # 最多显示5个匹配结果
                break
            
            template_name = match.get('template_name', 'Unknown')
            match_count = match.get('match_count', 0)
            quality = match.get('quality', 0.0)
            
            # 设置颜色
            if quality > 0.8:
                color = (0, 255, 0)  # 绿色
            elif quality > 0.5:
                color = (0, 255, 255)  # 黄色
            else:
                color = (0, 0, 255)  # 红色
            
            # 绘制文本
            text = f"{template_name}: {match_count} pts ({quality:.2f})"
            cv2.putText(annotated_frame, text, (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            y_offset += 25
        
        # 绘制模式信息
        mode = results.get('mode', 'unknown')
        mode_text = f"Mode: {mode}"
        cv2.putText(annotated_frame, mode_text, 
                   (annotated_frame.shape[1] - 150, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # 绘制匹配状态
        if results.get('success', False):
            status_text = "MATCH FOUND"
            color = (0, 255, 0)
        else:
            status_text = "NO MATCH"
            color = (0, 0, 255)
        
        cv2.putText(annotated_frame, status_text, 
                   (annotated_frame.shape[1] - 150, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        return annotated_frame
    
    def switch_mode(self, new_mode):
        """
        切换处理模式
        
        参数:
            new_mode: 新模式
        """
        valid_modes = ['hybrid', 'image', 'video']
        if new_mode in valid_modes:
            old_mode = self.mode
            self.mode = new_mode
            print(f"切换模式: {old_mode} -> {new_mode}")
            return True
        else:
            print(f"无效的模式: {new_mode}")
            return False
    
    def get_statistics(self):
        """获取统计信息"""
        if not self.match_history:
            return {}
        
        # 计算各种统计数据
        recent_history = self.match_history[-50:]  # 最近50条记录
        
        success_count = sum(1 for h in recent_history if h.get('matches'))
        total_count = len(recent_history)
        
        mode_counts = {}
        for h in recent_history:
            mode = h.get('mode', 'unknown')
            mode_counts[mode] = mode_counts.get(mode, 0) + 1
        
        return {
            'total_matches': len(self.match_history),
            'recent_success_rate': success_count / total_count if total_count > 0 else 0,
            'mode_distribution': mode_counts,
            'last_match_time': self.match_history[-1]['timestamp'] if self.match_history else None
        }

# 示例用法
if __name__ == "__main__":
    print("测试高级匹配器...")
    
    # 配置
    config = {
        'mode': 'hybrid',
        'primary_method': 'image',
        'fallback_to_video': True,
        'detector': {
            'confidence_threshold': 0.5
        },
        'image_matcher': {
            'feature_type': 'orb',
            'min_matches': 8
        },
        'video_matcher': {
            'frame_interval': 1,
            'min_confidence': 0.3
        }
    }
    
    # 创建高级匹配器
    matcher = AdvancedMatcher(config)
    
    # 加载模板
    image_dir = "data/images_material"
    count = matcher.load_templates(image_dir)
    print(f"共加载 {count} 个模板")
    
    # 测试摄像头
    print("\n启动摄像头测试...")
    print("按 'q' 退出，按 '1' 切换到图像模式，按 '2' 切换到视频模式，按 '3' 切换到混合模式")
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("无法打开摄像头")
        exit()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 处理帧
        results = matcher.process(frame)
        
        # 绘制结果
        annotated_frame = matcher.draw_results(frame, results)
        
        # 显示
        cv2.imshow('Advanced Matcher', annotated_frame)
        
        # 按键处理
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('1'):
            matcher.switch_mode('image')
        elif key == ord('2'):
            matcher.switch_mode('video')
        elif key == ord('3'):
            matcher.switch_mode('hybrid')
    
    cap.release()
    cv2.destroyAllWindows()
    
    # 打印统计信息
    stats = matcher.get_statistics()
    print(f"\n处理统计:")
    print(f"总匹配次数: {stats.get('total_matches', 0)}")
    print(f"最近成功率: {stats.get('recent_success_rate', 0)*100:.1f}%")
    print("模式分布:")
    for mode, count in stats.get('mode_distribution', {}).items():
        print(f"  {mode}: {count}")
#!/usr/bin/env python3
"""
视频匹配器模块
处理视频流中的图像匹配
"""
import cv2
import numpy as np
import time
from pathlib import Path
from image_matcher import ImageMatcher

class VideoMatcher:
    def __init__(self, config=None):
        """
        初始化视频匹配器
        
        参数:
            config: 配置字典
        """
        self.config = config or {}
        
        # 视频处理参数
        self.frame_interval = self.config.get('frame_interval', 1)  # 帧采样间隔
        self.min_confidence = self.config.get('min_confidence', 0.5)
        self.detection_interval = self.config.get('detection_interval', 1.0)  # 秒
        
        # 初始化图像匹配器
        self.image_matcher = ImageMatcher(config)
        
        # 状态变量
        self.last_detection_time = 0
        self.frame_count = 0
        self.current_matches = []
        
        print("视频匹配器初始化完成")
    
    def load_templates(self, dir_path):
        """
        加载模板
        
        参数:
            dir_path: 模板目录路径
            
        返回:
            加载的模板数量
        """
        return self.image_matcher.load_templates_from_dir(dir_path)
    
    def process_frame(self, frame):
        """
        处理视频帧
        
        参数:
            frame: 视频帧
            
        返回:
            result: 处理结果
        """
        current_time = time.time()
        self.frame_count += 1
        
        # 检查是否需要跳过此帧
        if self.frame_count % self.frame_interval != 0:
            return {'frame_processed': False, 'matches': []}
        
        # 检查是否到达检测间隔
        if current_time - self.last_detection_time < self.detection_interval:
            return {'frame_processed': False, 'matches': self.current_matches}
        
        # 执行图像匹配
        matches = self.image_matcher.match(frame)
        
        # 过滤低质量匹配
        filtered_matches = []
        for match in matches:
            if match['quality'] >= self.min_confidence:
                filtered_matches.append(match)
        
        # 更新状态
        self.current_matches = filtered_matches
        self.last_detection_time = current_time
        
        return {
            'frame_processed': True,
            'matches': filtered_matches,
            'frame_count': self.frame_count,
            'timestamp': current_time
        }
    
    def draw_results(self, frame, results):
        """
        在帧上绘制匹配结果
        
        参数:
            frame: 原始帧
            results: 处理结果
            
        返回:
            annotated_frame: 标注后的帧
        """
        annotated_frame = frame.copy()
        
        # 如果没有匹配结果，显示状态信息
        if not results['matches']:
            status_text = f"Frame: {self.frame_count} - No matches"
            cv2.putText(annotated_frame, status_text, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            return annotated_frame
        
        # 绘制每个匹配结果
        y_offset = 30
        for i, match in enumerate(results['matches']):
            # 文本信息
            text = f"{match['template_name']}: {match['match_count']} pts"
            
            # 根据质量设置颜色
            quality = match['quality']
            if quality > 0.8:
                color = (0, 255, 0)  # 绿色
            elif quality > 0.5:
                color = (0, 255, 255)  # 黄色
            else:
                color = (0, 0, 255)  # 红色
            
            # 绘制文本
            cv2.putText(annotated_frame, text, (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            y_offset += 25
        
        # 绘制帧计数
        fps_text = f"Frame: {self.frame_count}"
        cv2.putText(annotated_frame, fps_text, (10, annotated_frame.shape[0] - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return annotated_frame
    
    def process_video_file(self, video_path, output_path=None, show_preview=True):
        """
        处理视频文件
        
        参数:
            video_path: 视频文件路径
            output_path: 输出视频路径
            show_preview: 是否显示预览
            
        返回:
            statistics: 处理统计信息
        """
        print(f"开始处理视频: {video_path}")
        
        # 打开视频文件
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            print(f"无法打开视频文件: {video_path}")
            return None
        
        # 获取视频属性
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"视频信息: {width}x{height}, {fps} FPS, {total_frames} 帧")
        
        # 准备输出视频
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        else:
            out = None
        
        # 处理统计
        statistics = {
            'total_frames': total_frames,
            'processed_frames': 0,
            'detected_frames': 0,
            'products_found': [],
            'start_time': time.time()
        }
        
        frame_index = 0
        
        # 处理每一帧
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_index += 1
            
            # 处理帧
            results = self.process_frame(frame)
            
            # 更新统计信息
            statistics['processed_frames'] += 1
            if results['matches']:
                statistics['detected_frames'] += 1
                
                # 记录找到的商品
                for match in results['matches']:
                    if match['template_name'] not in statistics['products_found']:
                        statistics['products_found'].append(match['template_name'])
            
            # 绘制结果
            if show_preview or out:
                annotated_frame = self.draw_results(frame, results)
                
                # 显示预览
                if show_preview:
                    cv2.imshow('Video Matching', annotated_frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                
                # 写入输出视频
                if out:
                    out.write(annotated_frame)
            
            # 显示进度
            if frame_index % 100 == 0:
                progress = (frame_index / total_frames) * 100
                print(f"处理进度: {progress:.1f}% ({frame_index}/{total_frames})")
        
        # 完成统计
        statistics['end_time'] = time.time()
        statistics['processing_time'] = statistics['end_time'] - statistics['start_time']
        
        # 清理资源
        cap.release()
        if out:
            out.release()
        cv2.destroyAllWindows()
        
        print(f"视频处理完成: {video_path}")
        self.print_statistics(statistics)
        
        return statistics
    
    def process_camera(self, camera_id=0, duration=None):
        """
        处理摄像头视频流
        
        参数:
            camera_id: 摄像头ID
            duration: 处理时长（秒）
        """
        print(f"打开摄像头 {camera_id}...")
        
        cap = cv2.VideoCapture(camera_id)
        if not cap.isOpened():
            print(f"无法打开摄像头 {camera_id}")
            return
        
        print("摄像头已打开。按 'q' 退出，按 's' 保存截图")
        
        start_time = time.time()
        frame_count = 0
        
        while True:
            # 检查处理时长
            if duration and (time.time() - start_time) > duration:
                print(f"达到处理时长: {duration}秒")
                break
            
            ret, frame = cap.read()
            if not ret:
                print("无法读取摄像头画面")
                break
            
            frame_count += 1
            
            # 处理帧
            results = self.process_frame(frame)
            
            # 绘制结果
            annotated_frame = self.draw_results(frame, results)
            
            # 显示
            cv2.imshow('Live Video Matching', annotated_frame)
            
            # 按键处理
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                # 保存截图
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"outputs/screenshot_{timestamp}.jpg"
                Path("outputs").mkdir(exist_ok=True)
                cv2.imwrite(filename, annotated_frame)
                print(f"截图已保存: {filename}")
        
        # 清理
        cap.release()
        cv2.destroyAllWindows()
        
        print(f"摄像头处理完成。总帧数: {frame_count}")
    
    def print_statistics(self, stats):
        """打印统计信息"""
        print("\n" + "=" * 50)
        print("视频处理统计")
        print("=" * 50)
        print(f"总帧数: {stats['total_frames']}")
        print(f"处理帧数: {stats['processed_frames']}")
        print(f"检测到目标的帧数: {stats['detected_frames']}")
        print(f"检测率: {(stats['detected_frames']/stats['processed_frames']*100):.1f}%")
        print(f"找到的商品: {', '.join(stats['products_found'])}")
        print(f"处理时间: {stats['processing_time']:.1f}秒")
        print(f"平均FPS: {stats['processed_frames']/stats['processing_time']:.1f}")

# 示例用法
if __name__ == "__main__":
    # 创建视频匹配器
    matcher = VideoMatcher({
        'frame_interval': 2,
        'min_confidence': 0.3,
        'detection_interval': 0.5
    })
    
    # 加载模板
    template_dir = "data/images_material"
    if Path(template_dir).exists():
        count = matcher.load_templates(template_dir)
        print(f"加载了 {count} 个模板")
    else:
        print(f"模板目录不存在: {template_dir}")
        print("请将商品图片放入 data/images_material 目录")
    
    # 测试摄像头
    print("\n测试摄像头匹配...")
    matcher.process_camera(0, duration=10)  # 处理10秒
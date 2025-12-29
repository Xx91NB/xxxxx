#!/usr/bin/env python3
"""
智能系统核心 (简化版)
"""
import cv2
import numpy as np
from pathlib import Path

class IntelligentSystem:
    def __init__(self, config_path="config/default.yaml"):
        """
        初始化智能系统
        """
        print("智能系统初始化...")
        
        # 加载配置
        self.config = self._load_config(config_path)
        
        # 初始化组件
        self._init_components()
        
        print("智能系统初始化完成")
    
    def _load_config(self, config_path):
        """加载配置文件"""
        config_file = Path(config_path)
        if not config_file.exists():
            return {}
        
        try:
            import yaml
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except:
            return {}
    
    def _init_components(self):
        """初始化组件"""
        try:
            from detector import ProductDetector
            from image_matcher import ImageMatcher
            
            self.detector = ProductDetector()
            self.matcher = ImageMatcher()
            
            print("✓ 组件初始化完成")
        except ImportError as e:
            print(f"组件初始化失败: {e}")
    
    def run_with_gui(self, camera_id=0):
        """运行带GUI的系统"""
        print(f"启动GUI模式，摄像头ID: {camera_id}")
        
        # 尝试打开摄像头
        cap = cv2.VideoCapture(camera_id)
        if not cap.isOpened():
            print("无法打开摄像头，尝试其他ID...")
            for i in [1, 2, 3]:
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    print(f"打开摄像头 {i}")
                    break
                cap.release()
            else:
                print("无法打开任何摄像头")
                return
        
        print("按 'q' 退出，按 's' 保存截图")
        
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # 处理帧
            # 这里可以添加您的处理逻辑
            
            # 绘制界面
            h, w = frame.shape[:2]
            
            # 绘制中心区域
            cv2.rectangle(frame, (w//4, h//4), (3*w//4, 3*h//4), (0, 255, 0), 2)
            
            # 添加文字
            cv2.putText(frame, "智能商品识别系统", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Frame: {frame_count}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            cv2.putText(frame, "Press 'q' to quit", (10, 90),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            cv2.imshow("Intelligent System", frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                # 保存截图
                import time
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"outputs/screenshot_{timestamp}.jpg"
                Path("outputs").mkdir(exist_ok=True)
                cv2.imwrite(filename, frame)
                print(f"截图已保存: {filename}")
        
        cap.release()
        cv2.destroyAllWindows()
        print(f"处理完成，共 {frame_count} 帧")

if __name__ == "__main__":
    # 测试系统
    system = IntelligentSystem()
    system.run_with_gui(0)
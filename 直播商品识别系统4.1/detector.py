#!/usr/bin/env python3
"""
商品检测器模块
"""
import cv2
import numpy as np
from pathlib import Path

class ProductDetector:
    def __init__(self, config=None):
        """初始化商品检测器"""
        self.config = config or {}
        print("商品检测器初始化...")
        
        # 加载Haar级联分类器用于人脸检测（作为示例）
        self.face_cascade = None
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        
        if Path(cascade_path).exists():
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            print("加载了Haar级联分类器")
        else:
            print("警告: 未找到Haar级联分类器文件")
    
    def detect(self, image):
        """
        检测图像中的商品（这里使用人脸检测作为示例）
        
        参数:
            image: 输入图像 (numpy数组)
            
        返回:
            detections: 检测结果列表
        """
        if self.face_cascade is None:
            # 返回模拟结果
            return self.mock_detections(image)
        
        # 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 检测人脸（这里作为商品检测的示例）
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        detections = []
        for (x, y, w, h) in faces:
            detections.append({
                'class': 'product',
                'confidence': 0.8,  # 模拟置信度
                'bbox': [x, y, w, h],
                'label': '商品示例'
            })
        
        return detections
    
    def mock_detections(self, image):
        """生成模拟检测结果（用于测试）"""
        height, width = image.shape[:2]
        
        # 在图像中心生成一个模拟检测框
        center_x, center_y = width // 2, height // 2
        box_size = min(width, height) // 4
        
        return [{
            'class': 'product',
            'confidence': 0.75,
            'bbox': [
                center_x - box_size // 2,
                center_y - box_size // 2,
                box_size,
                box_size
            ],
            'label': '模拟商品'
        }]
    
    def draw_detections(self, image, detections):
        """在图像上绘制检测结果"""
        result = image.copy()
        
        for det in detections:
            x, y, w, h = det['bbox']
            confidence = det['confidence']
            label = det['label']
            
            # 绘制矩形框
            color = (0, 255, 0)  # 绿色
            cv2.rectangle(result, (x, y), (x + w, y + h), color, 2)
            
            # 绘制标签
            label_text = f"{label}: {confidence:.2f}"
            cv2.putText(result, label_text, (x, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return result
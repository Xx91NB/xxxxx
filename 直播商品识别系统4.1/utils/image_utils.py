#!/usr/bin/env python3
"""
图像处理工具函数
解决OpenCV中文路径等问题
"""
import os
import cv2
import numpy as np
from pathlib import Path
from PIL import Image, ImageFile

# 允许加载截断的图片
ImageFile.LOAD_TRUNCATED_IMAGES = True

def read_image(path):
    """
    读取图像文件，支持中文路径
    
    参数:
        path: 图像文件路径
        
    返回:
        image: OpenCV格式的图像 (BGR)
    """
    try:
        path = str(path)
        
        # 方法1: 先尝试使用OpenCV读取
        img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)
        if img is not None:
            return img
        
        # 方法2: 使用PIL读取并转换
        img_pil = Image.open(path)
        # 转换为RGB（如果是RGBA，去掉alpha通道）
        if img_pil.mode == 'RGBA':
            img_pil = img_pil.convert('RGB')
        elif img_pil.mode != 'RGB':
            img_pil = img_pil.convert('RGB')
        
        # 转换为numpy数组
        img_array = np.array(img_pil)
        # PIL是RGB，OpenCV是BGR，需要转换
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        return img_bgr
        
    except Exception as e:
        print(f"读取图像失败 {path}: {e}")
        return None

def save_image(image, path):
    """
    保存图像文件，支持中文路径
    
    参数:
        image: OpenCV格式的图像 (BGR)
        path: 保存路径
    """
    try:
        path = str(path)
        
        # 确保目录存在
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # 方法1: 使用cv2.imencode
        success, buffer = cv2.imencode('.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, 95])
        if success:
            buffer.tofile(path)
            return True
        
        # 方法2: 使用PIL保存
        # 转换BGR到RGB
        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        img_pil.save(path, quality=95)
        
        return True
        
    except Exception as e:
        print(f"保存图像失败 {path}: {e}")
        return False

def resize_image(image, max_size=800):
    """
    调整图像大小，保持宽高比
    
    参数:
        image: 输入图像
        max_size: 最大边长
        
    返回:
        resized_image: 调整后的图像
    """
    h, w = image.shape[:2]
    
    # 计算缩放比例
    if h > w:
        new_h = max_size
        new_w = int(w * max_size / h)
    else:
        new_w = max_size
        new_h = int(h * max_size / w)
    
    # 调整大小
    resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
    return resized

def show_image(image, window_name='Image', wait_time=0):
    """
    显示图像，支持中文窗口名
    
    参数:
        image: 图像
        window_name: 窗口名称
        wait_time: 等待时间（0表示无限等待）
    """
    # 创建一个简单的显示函数
    cv2.imshow(window_name, image)
    cv2.waitKey(wait_time)

def get_image_files(directory, extensions=['.jpg', '.jpeg', '.png', '.bmp']):
    """
    获取目录中的所有图像文件
    
    参数:
        directory: 目录路径
        extensions: 支持的扩展名
        
    返回:
        图像文件路径列表
    """
    directory = Path(directory)
    image_files = []
    
    for ext in extensions:
        image_files.extend(directory.glob(f'*{ext}'))
        image_files.extend(directory.glob(f'*{ext.upper()}'))
    
    return image_files

def extract_roi(image, roi):
    """
    从图像中提取感兴趣区域
    
    参数:
        image: 原始图像
        roi: 区域 (x, y, w, h)
        
    返回:
        roi_image: 提取的区域
    """
    x, y, w, h = roi
    return image[y:y+h, x:x+w]

def draw_text(image, text, position, color=(0, 255, 0), font_scale=0.6, thickness=2):
    """
    在图像上绘制文本
    
    参数:
        image: 图像
        text: 文本内容
        position: 位置 (x, y)
        color: 颜色 (B, G, R)
        font_scale: 字体大小
        thickness: 线条粗细
    """
    cv2.putText(image, text, position, 
                cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)

def draw_rectangle(image, rect, color=(0, 255, 0), thickness=2):
    """
    在图像上绘制矩形
    
    参数:
        image: 图像
        rect: 矩形 (x, y, w, h)
        color: 颜色 (B, G, R)
        thickness: 线条粗细
    """
    x, y, w, h = rect
    cv2.rectangle(image, (x, y), (x+w, y+h), color, thickness)
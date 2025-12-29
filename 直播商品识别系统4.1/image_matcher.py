#!/usr/bin/env python3
"""
图像匹配器模块
使用ORB特征进行图像匹配
"""
import cv2
import numpy as np
from pathlib import Path
import os

class ImageMatcher:
    def __init__(self, config=None):
        """
        初始化图像匹配器
        
        参数:
            config: 配置字典
        """
        self.config = config or {}
        
        # 设置匹配器参数
        self.feature_type = self.config.get('feature_type', 'orb')  # orb, sift, brisk
        self.match_ratio = self.config.get('match_ratio', 0.75)
        self.min_matches = self.config.get('min_matches', 10)
        self.use_flann = self.config.get('use_flann', True)
        
        # 初始化特征检测器
        self.detector = self._init_detector()
        
        # 初始化匹配器
        if self.use_flann:
            # FLANN匹配器参数
            FLANN_INDEX_KDTREE = 1
            index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
            search_params = dict(checks=50)
            self.matcher = cv2.FlannBasedMatcher(index_params, search_params)
        else:
            # 暴力匹配器
            self.matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        
        # 存储模板特征
        self.templates = {}
        print(f"图像匹配器初始化完成 - 特征类型: {self.feature_type}")
    
    def _init_detector(self):
        """初始化特征检测器"""
        if self.feature_type.lower() == 'orb':
            return cv2.ORB_create(nfeatures=1000)
        elif self.feature_type.lower() == 'sift':
            return cv2.SIFT_create()
        elif self.feature_type.lower() == 'brisk':
            return cv2.BRISK_create()
        elif self.feature_type.lower() == 'akaze':
            return cv2.AKAZE_create()
        else:
            print(f"未知特征类型: {self.feature_type}，使用默认ORB")
            return cv2.ORB_create(nfeatures=1000)
    
    def extract_features(self, image):
        """
        提取图像特征
        
        参数:
            image: 输入图像
            
        返回:
            keypoints: 关键点
            descriptors: 描述符
        """
        if image is None:
            return None, None
        
        # 转换为灰度图
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # 提取特征
        keypoints, descriptors = self.detector.detectAndCompute(gray, None)
        
        return keypoints, descriptors
    
    def add_template(self, name, image):
        """
        添加模板图像
        
        参数:
            name: 模板名称
            image: 模板图像
        """
        keypoints, descriptors = self.extract_features(image)
        
        if descriptors is not None:
            self.templates[name] = {
                'keypoints': keypoints,
                'descriptors': descriptors,
                'image': image
            }
            print(f"添加模板: {name} - 特征点数: {len(keypoints)}")
            return True
        else:
            print(f"无法从图像中提取特征: {name}")
            return False
    
    def load_templates_from_dir(self, dir_path):
        """
        从目录加载模板图像
        
        参数:
            dir_path: 目录路径
            
        返回:
            count: 加载的模板数量
        """
        dir_path = Path(dir_path)
        if not dir_path.exists():
            print(f"模板目录不存在: {dir_path}")
            return 0
        
        count = 0
        # 支持的图像格式
        extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        
        for ext in extensions:
            for img_file in dir_path.glob(f'*{ext}'):
                try:
                    # 读取图像
                    image = cv2.imread(str(img_file))
                    if image is None:
                        continue
                    
                    # 使用文件名（不含扩展名）作为模板名
                    name = img_file.stem
                    
                    # 添加模板
                    if self.add_template(name, image):
                        count += 1
                        
                except Exception as e:
                    print(f"加载模板失败 {img_file}: {e}")
        
        print(f"从 {dir_path} 加载了 {count} 个模板")
        return count
    
    def match(self, query_image, template_name=None):
        """
        匹配查询图像与模板
        
        参数:
            query_image: 查询图像
            template_name: 指定模板名称，None表示匹配所有模板
            
        返回:
            matches: 匹配结果列表
        """
        # 提取查询图像特征
        query_kp, query_desc = self.extract_features(query_image)
        
        if query_desc is None:
            return []
        
        results = []
        
        # 确定要匹配的模板
        if template_name:
            templates_to_match = [(template_name, self.templates[template_name])] \
                if template_name in self.templates else []
        else:
            templates_to_match = self.templates.items()
        
        for name, template in templates_to_match:
            if template['descriptors'] is None:
                continue
            
            try:
                if self.use_flann:
                    # FLANN匹配
                    matches = self.matcher.knnMatch(
                        query_desc, 
                        template['descriptors'], 
                        k=2
                    )
                    
                    # 应用Lowe's比率测试
                    good_matches = []
                    for m, n in matches:
                        if m.distance < self.match_ratio * n.distance:
                            good_matches.append(m)
                    
                    match_count = len(good_matches)
                    
                else:
                    # 暴力匹配
                    matches = self.matcher.match(query_desc, template['descriptors'])
                    matches = sorted(matches, key=lambda x: x.distance)
                    
                    # 取前N个最佳匹配
                    match_count = len(matches)
                    good_matches = matches[:min(50, match_count)]
                
                # 计算匹配质量
                if match_count > 0:
                    # 简单的匹配质量评分
                    quality = min(1.0, match_count / 100.0)
                    
                    # 计算平均距离（距离越小越好）
                    if good_matches:
                        avg_distance = np.mean([m.distance for m in good_matches])
                    else:
                        avg_distance = 999
                    
                    # 检查是否满足最小匹配数要求
                    if match_count >= self.min_matches:
                        results.append({
                            'template_name': name,
                            'match_count': match_count,
                            'good_matches': good_matches,
                            'quality': quality,
                            'avg_distance': avg_distance,
                            'keypoints': query_kp,
                            'template_keypoints': template['keypoints'],
                            'success': True
                        })
                        
            except Exception as e:
                print(f"匹配模板 {name} 时出错: {e}")
        
        # 按质量排序
        results.sort(key=lambda x: (x['match_count'], -x['avg_distance']), reverse=True)
        
        return results
    
    def draw_matches(self, query_image, match_result, max_matches=20):
        """
        绘制匹配结果
        
        参数:
            query_image: 查询图像
            match_result: 匹配结果
            max_matches: 最多显示的匹配点数量
            
        返回:
            绘制了匹配结果的图像
        """
        if not match_result['success']:
            return query_image
        
        # 获取模板图像
        template = self.templates.get(match_result['template_name'], None)
        if template is None:
            return query_image
        
        # 选择要显示的匹配点
        good_matches = match_result['good_matches']
        if len(good_matches) > max_matches:
            display_matches = good_matches[:max_matches]
        else:
            display_matches = good_matches
        
        # 绘制匹配
        result_img = cv2.drawMatches(
            query_image, match_result['keypoints'],
            template['image'], template['keypoints'],
            display_matches, None,
            flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS
        )
        
        # 添加文本信息
        info_text = f"{match_result['template_name']}: {match_result['match_count']} matches"
        cv2.putText(result_img, info_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        return result_img
    
    def match_best(self, query_image):
        """
        查找最佳匹配
        
        参数:
            query_image: 查询图像
            
        返回:
            best_match: 最佳匹配结果或None
        """
        matches = self.match(query_image)
        
        if matches:
            return matches[0]
        else:
            return None

# 示例用法
if __name__ == "__main__":
    # 创建匹配器
    matcher = ImageMatcher({
        'feature_type': 'orb',
        'match_ratio': 0.75,
        'min_matches': 10
    })
    
    # 加载模板
    template_dir = "data/images_material"
    if Path(template_dir).exists():
        matcher.load_templates_from_dir(template_dir)
    else:
        print(f"模板目录不存在: {template_dir}")
    
    print("图像匹配器测试完成")
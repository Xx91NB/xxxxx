#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
输出管理器
统一管理所有txt文档输出
"""
import os
import json
import time
from datetime import datetime
from pathlib import Path

class OutputManager:
    def __init__(self, root_dir="."):
        """初始化输出管理器"""
        self.root_dir = Path(root_dir)
        
        # 定义所有输出文件
        self.output_files = {
            'current_product': self.root_dir / "outputs" / "current_product.txt",
            'recognition_log': self.root_dir / "outputs" / "recognition_log.txt",
            'learning_log': self.root_dir / "outputs" / "learning_log.txt",
            'system_log': self.root_dir / "outputs" / "system_log.txt",
            'statistics': self.root_dir / "outputs" / "statistics.txt",
            'screen_recognition': self.root_dir / "outputs" / "screen_recognition_log.txt"
        }
        
        # 确保输出目录存在
        self._ensure_dirs()
        
        # 确保所有文件存在
        self._init_output_files()
        
        print(f"输出管理器初始化完成，输出目录: {self.root_dir / 'outputs'}")
    
    def _ensure_dirs(self):
        """确保所有目录存在"""
        # 确保输出目录存在
        (self.root_dir / "outputs").mkdir(exist_ok=True)
    
    def _init_output_files(self):
        """初始化输出文件"""
        for name, file_path in self.output_files.items():
            if not file_path.exists():
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        if name == 'current_product':
                            f.write("当前识别商品: 无\n")
                            f.write("最后更新时间: -\n")
                            f.write("置信度: 0.00%\n")
                            f.write("=" * 40 + "\n")
                        elif name == 'statistics':
                            f.write("系统统计信息\n")
                            f.write("=" * 50 + "\n")
                            f.write("创建时间: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n")
                            f.write("=" * 50 + "\n\n")
                        else:
                            f.write(f"{name.replace('_', ' ').title()} 日志\n")
                            f.write("=" * 50 + "\n")
                            f.write(f"创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                            f.write("=" * 50 + "\n\n")
                except Exception as e:
                    print(f"初始化文件 {name} 失败: {e}")
    
    def update_current_product(self, product_name, confidence=0.0, frame_info=None):
        """
        更新当前识别商品
        
        参数:
            product_name: 商品名称
            confidence: 置信度
            frame_info: 帧信息
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            content = f"""当前识别商品: {product_name}
置信度: {confidence:.2%}
识别时间: {timestamp}
"""
            if frame_info:
                content += f"帧信息: {frame_info}\n"
            
            content += "\n" + "=" * 40 + "\n"
            
            with open(self.output_files['current_product'], 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"更新当前商品: {product_name} ({confidence:.2%})")
            
            # 同时记录到识别日志
            self.log_recognition(product_name, confidence, "更新当前商品")
        except Exception as e:
            print(f"更新当前商品失败: {e}")
    
    def log_recognition(self, product_name, confidence, action="识别"):
        """
        记录识别日志
        
        参数:
            product_name: 商品名称
            confidence: 置信度
            action: 操作类型
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            log_entry = f"[{timestamp}] {action}: {product_name} (置信度: {confidence:.2%})\n"
            
            with open(self.output_files['recognition_log'], 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"记录识别日志失败: {e}")
    
    def log_learning(self, product_name, action_type="自动学习", reason="", image_path=""):
        """
        记录学习日志
        
        参数:
            product_name: 商品名称
            action_type: 学习类型 (自动/手动)
            reason: 学习原因
            image_path: 图片保存路径
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            log_entry = f"[{timestamp}] {action_type}: {product_name}\n"
            if reason:
                log_entry += f"        原因: {reason}\n"
            if image_path:
                log_entry += f"        图片: {image_path}\n"
            log_entry += "\n"
            
            with open(self.output_files['learning_log'], 'a', encoding='utf-8') as f:
                f.write(log_entry)
                
            print(f"记录学习日志: {product_name} ({action_type})")
        except Exception as e:
            print(f"记录学习日志失败: {e}")
    
    def log_system(self, module, message, level="INFO"):
        """
        记录系统日志
        
        参数:
            module: 模块名称
            message: 日志消息
            level: 日志级别
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            log_entry = f"[{timestamp}] [{level}] [{module}] {message}\n"
            
            with open(self.output_files['system_log'], 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"记录系统日志失败: {e}")
    
    def update_statistics(self, stats_data):
        """
        更新统计信息
        
        参数:
            stats_data: 统计字典
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            content = f"系统统计信息 (更新于: {timestamp})\n"
            content += "=" * 50 + "\n\n"
            
            if isinstance(stats_data, dict):
                for section, data in stats_data.items():
                    if isinstance(data, dict):
                        content += f"{section}:\n"
                        for key, value in data.items():
                            content += f"  {key}: {value}\n"
                    else:
                        content += f"{section}: {data}\n"
                    
                    content += "\n"
            else:
                content += f"统计数据: {stats_data}\n"
            
            content += "=" * 50 + "\n"
            
            with open(self.output_files['statistics'], 'w', encoding='utf-8') as f:
                f.write(content)
                
            print(f"更新统计信息完成")
        except Exception as e:
            print(f"更新统计信息失败: {e}")
    
    def log_screen_recognition(self, product_name, confidence, screen_region=None, test_mode=False):
        """
        记录屏幕识别日志
        
        参数:
            product_name: 商品名称
            confidence: 置信度
            screen_region: 屏幕区域
            test_mode: 是否为测试模式
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            prefix = "[测试]" if test_mode else ""
            log_entry = f"[{timestamp}] {prefix}屏幕识别: {product_name} (置信度: {confidence:.2%})\n"
            if screen_region:
                log_entry += f"        屏幕区域: {screen_region}\n"
            log_entry += "\n"
            
            with open(self.output_files['screen_recognition'], 'a', encoding='utf-8') as f:
                f.write(log_entry)
                
            print(f"记录屏幕识别: {product_name} ({confidence:.2%})")
        except Exception as e:
            print(f"记录屏幕识别日志失败: {e}")
    
    def get_current_product(self):
        """获取当前识别商品"""
        try:
            with open(self.output_files['current_product'], 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            print(f"获取当前商品失败: {e}")
            return "无当前商品"
    
    def get_recent_recognitions(self, count=10):
        """获取最近的识别记录"""
        try:
            with open(self.output_files['recognition_log'], 'r', encoding='utf-8') as f:
                lines = f.readlines()
                return lines[-count:] if len(lines) >= count else lines
        except Exception as e:
            print(f"获取最近识别记录失败: {e}")
            return ["无识别记录"]
    
    def get_learning_summary(self):
        """获取学习摘要"""
        try:
            with open(self.output_files['learning_log'], 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
                # 统计学习数量
                auto_count = 0
                manual_count = 0
                for line in lines:
                    if "自动学习" in line:
                        auto_count += 1
                    elif "手动学习" in line:
                        manual_count += 1
                
                return {
                    'total_learned': auto_count + manual_count,
                    'auto_learned': auto_count,
                    'manual_learned': manual_count,
                    'last_learning': lines[-1] if lines else "无学习记录"
                }
        except Exception as e:
            print(f"获取学习摘要失败: {e}")
            return {'total_learned': 0, 'auto_learned': 0, 'manual_learned': 0, 'last_learning': '无学习记录'}
    
    def clear_logs(self, log_type="all"):
        """
        清空日志
        
        参数:
            log_type: 日志类型 (all, recognition, learning, system)
        """
        try:
            if log_type == "all":
                for name, file_path in self.output_files.items():
                    if name != 'statistics':  # 不清空统计文件
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(f"{name.replace('_', ' ').title()} 日志 (已清空)\n")
                            f.write("=" * 50 + "\n")
                            f.write(f"清空时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                            f.write("=" * 50 + "\n\n")
                print("所有日志已清空")
                return True
            elif log_type in ['recognition', 'learning', 'system', 'screen_recognition']:
                if log_type == 'screen_recognition':
                    file_key = 'screen_recognition'
                else:
                    file_key = f"{log_type}_log"
                    
                if file_key in self.output_files:
                    file_path = self.output_files[file_key]
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(f"{log_type.title()} 日志 (已清空)\n")
                        f.write("=" * 50 + "\n")
                        f.write(f"清空时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write("=" * 50 + "\n\n")
                    print(f"{log_type}日志已清空")
                    return True
                else:
                    print(f"日志类型 {log_type} 不存在")
                    return False
            else:
                print(f"不支持的日志类型: {log_type}")
                return False
        except Exception as e:
            print(f"清空日志失败: {e}")
            return False

# 全局实例
_output_manager = None

def get_output_manager(root_dir="."):
    """获取输出管理器实例"""
    global _output_manager
    if _output_manager is None:
        _output_manager = OutputManager(root_dir)
    return _output_manager

# 测试代码
if __name__ == "__main__":
    print("测试输出管理器...")
    mgr = get_output_manager()
    
    # 测试各种功能
    mgr.log_system("Test", "开始测试输出管理器")
    mgr.update_current_product("测试商品", 0.95, "测试环境")
    mgr.log_recognition("测试商品1", 0.85)
    mgr.log_learning("测试商品2", "自动学习", "测试学习", "test.jpg")
    mgr.log_screen_recognition("屏幕测试商品", 0.91, "1920x1080")
    
    # 更新统计信息
    stats = {
        "系统状态": {
            "运行时间": "10分钟",
            "识别次数": 5,
            "学习次数": 2
        },
        "性能指标": {
            "平均置信度": "85%",
            "识别速度": "15帧/秒"
        }
    }
    mgr.update_statistics(stats)
    
    print("测试完成！")
    print("输出文件列表:")
    for name, path in mgr.output_files.items():
        print(f"  {name}: {path}")
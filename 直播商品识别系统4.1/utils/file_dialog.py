#!/usr/bin/env python3
"""
文件对话框工具
解决中文路径和跨平台问题
"""
import os
from pathlib import Path
import tkinter as tk
from tkinter import filedialog

class FileDialog:
    def __init__(self):
        self.root = None
    
    def _get_root(self):
        """获取或创建根窗口"""
        if self.root is None:
            self.root = tk.Tk()
            self.root.withdraw()  # 隐藏主窗口
        return self.root
    
    def select_image_file(self, title="选择图像文件"):
        """
        选择图像文件
        
        参数:
            title: 对话框标题
            
        返回:
            选择的文件路径，或None
        """
        try:
            root = self._get_root()
            
            file_path = filedialog.askopenfilename(
                title=title,
                filetypes=[
                    ("所有图像文件", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif"),
                    ("JPEG 文件", "*.jpg *.jpeg"),
                    ("PNG 文件", "*.png"),
                    ("BMP 文件", "*.bmp"),
                    ("所有文件", "*.*")
                ]
            )
            
            if file_path:
                return Path(file_path)
            else:
                return None
                
        except Exception as e:
            print(f"选择文件失败: {e}")
            return self.select_image_file_simple()
    
    def select_directory(self, title="选择目录"):
        """
        选择目录
        
        参数:
            title: 对话框标题
            
        返回:
            选择的目录路径，或None
        """
        try:
            root = self._get_root()
            
            dir_path = filedialog.askdirectory(title=title)
            
            if dir_path:
                return Path(dir_path)
            else:
                return None
                
        except Exception as e:
            print(f"选择目录失败: {e}")
            return self.select_directory_simple()
    
    def select_image_file_simple(self):
        """简单的文件选择（无GUI）"""
        while True:
            file_path = input("请输入图像文件路径 (或输入 'q' 取消): ").strip()
            
            if file_path.lower() == 'q':
                return None
            
            path = Path(file_path)
            if path.exists() and path.is_file():
                return path
            else:
                print("文件不存在，请重新输入")
    
    def select_directory_simple(self):
        """简单的目录选择（无GUI）"""
        while True:
            dir_path = input("请输入目录路径 (或输入 'q' 取消): ").strip()
            
            if dir_path.lower() == 'q':
                return None
            
            path = Path(dir_path)
            if path.exists() and path.is_dir():
                return path
            else:
                print("目录不存在，请重新输入")
    
    def cleanup(self):
        """清理资源"""
        if self.root:
            self.root.destroy()
            self.root = None

# 全局实例
_file_dialog = None

def get_file_dialog():
    """获取文件对话框实例"""
    global _file_dialog
    if _file_dialog is None:
        _file_dialog = FileDialog()
    return _file_dialog

def select_image_file(title="选择图像文件"):
    """选择图像文件（快捷函数）"""
    dialog = get_file_dialog()
    return dialog.select_image_file(title)

def select_directory(title="选择目录"):
    """选择目录（快捷函数）"""
    dialog = get_file_dialog()
    return dialog.select_directory(title)

def cleanup_file_dialog():
    """清理文件对话框资源"""
    global _file_dialog
    if _file_dialog:
        _file_dialog.cleanup()
        _file_dialog = None
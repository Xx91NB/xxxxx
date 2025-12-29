#!/usr/bin/env python3
"""
屏幕区域校准工具
"""
import cv2
import yaml
from pathlib import Path

class Calibrator:
    def __init__(self):
        """初始化校准器"""
        print("初始化屏幕校准器...")
        self.region = None
        
    def run(self):
        """运行校准程序"""
        print("\n=== 屏幕区域校准 ===")
        print("提示: 使用鼠标拖动选择屏幕区域，按Enter确认，按ESC取消")
        
        # 获取屏幕截图
        try:
            # 尝试使用多种方法获取屏幕
            screen = self.capture_screen()
            if screen is None:
                print("无法获取屏幕截图，请检查权限")
                return
        except Exception as e:
            print(f"获取屏幕截图失败: {e}")
            return
        
        # 选择区域
        roi = cv2.selectROI("选择屏幕区域 (按Enter确认, ESC取消)", screen, False)
        cv2.destroyAllWindows()
        
        if roi[2] > 0 and roi[3] > 0:
            self.region = roi
            self.save_config()
            print(f"校准完成！区域: {roi}")
        else:
            print("校准取消")
    
    def capture_screen(self):
        """捕获屏幕"""
        try:
            # 方法1: 使用mss（如果可用）
            try:
                from mss import mss
                with mss() as sct:
                    monitor = sct.monitors[1]  # 第二台显示器
                    screenshot = sct.grab(monitor)
                    import numpy as np
                    img = np.array(screenshot)
                    # 转换BGR到RGB
                    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                    return img
            except ImportError:
                print("mss模块未安装，尝试其他方法...")
            
            # 方法2: 使用pyautogui
            try:
                import pyautogui
                screenshot = pyautogui.screenshot()
                img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                return img
            except ImportError:
                print("pyautogui模块未安装，尝试其他方法...")
            
            # 方法3: 使用摄像头模拟
            print("使用摄像头模拟屏幕...")
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                ret, frame = cap.read()
                cap.release()
                if ret:
                    return frame
            
            return None
            
        except Exception as e:
            print(f"捕获屏幕时出错: {e}")
            return None
    
    def save_config(self):
        """保存校准配置"""
        config = {
            'screen': {
                'region': {
                    'x': int(self.region[0]),
                    'y': int(self.region[1]),
                    'width': int(self.region[2]),
                    'height': int(self.region[3])
                }
            },
            'calibration': {
                'timestamp': '2025-12-29',
                'version': '1.0'
            }
        }
        
        # 确保config目录存在
        Path("config").mkdir(exist_ok=True)
        
        # 保存为YAML文件
        config_file = Path("config/calibration.yaml")
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        
        print(f"配置已保存到: {config_file}")

if __name__ == "__main__":
    calibrator = Calibrator()
    calibrator.run()
    input("\n按任意键退出...")
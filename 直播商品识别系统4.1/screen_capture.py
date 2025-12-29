#!/usr/bin/env python3
"""
屏幕捕获模块
用于捕获桌面屏幕进行视频识别
"""
import cv2
import numpy as np
import time
from pathlib import Path

class ScreenCapture:
    def __init__(self, region=None, capture_method='mss'):
        """
        初始化屏幕捕获器
        
        参数:
            region: 捕获区域 (x, y, width, height)
            capture_method: 捕获方法 ('mss', 'pyautogui', 'dxcam')
        """
        self.region = region
        self.capture_method = capture_method
        self.capturing = False
        
        # 初始化捕获器
        self._init_capturer()
        
        print(f"屏幕捕获器初始化 - 方法: {capture_method}")
    
    def _init_capturer(self):
        """初始化屏幕捕获器"""
        try:
            if self.capture_method == 'mss':
                from mss import mss
                self.sct = mss()
                print("✓ 使用 mss 进行屏幕捕获")
                
            elif self.capture_method == 'pyautogui':
                import pyautogui
                self.pyautogui = pyautogui
                print("✓ 使用 pyautogui 进行屏幕捕获")
                
            elif self.capture_method == 'dxcam':
                try:
                    import dxcam
                    self.camera = dxcam.create()
                    print("✓ 使用 dxcam 进行屏幕捕获")
                except ImportError:
                    print("dxcam 未安装，回退到 mss")
                    self.capture_method = 'mss'
                    from mss import mss
                    self.sct = mss()
                    
        except ImportError as e:
            print(f"导入捕获库失败: {e}")
            print("正在安装 mss...")
            import subprocess
            subprocess.check_call(['pip', 'install', 'mss'])
            from mss import mss
            self.sct = mss()
            self.capture_method = 'mss'
    
    def get_screen_size(self):
        """获取屏幕尺寸"""
        try:
            if self.capture_method == 'mss':
                monitor = self.sct.monitors[1]  # 主显示器
                return {
                    'width': monitor['width'],
                    'height': monitor['height'],
                    'left': monitor['left'],
                    'top': monitor['top']
                }
            elif self.capture_method == 'pyautogui':
                import pyautogui
                width, height = pyautogui.size()
                return {'width': width, 'height': height, 'left': 0, 'top': 0}
            else:
                # 默认值
                return {'width': 1920, 'height': 1080, 'left': 0, 'top': 0}
        except:
            return {'width': 1920, 'height': 1080, 'left': 0, 'top': 0}
    
    def capture(self, region=None):
        """
        捕获屏幕区域
        
        参数:
            region: 捕获区域 (x, y, width, height)，None表示全屏
            
        返回:
            捕获的图像 (OpenCV格式)
        """
        capture_region = region or self.region
        
        try:
            if self.capture_method == 'mss':
                # 使用mss捕获
                if capture_region:
                    monitor = {
                        "left": capture_region[0],
                        "top": capture_region[1],
                        "width": capture_region[2],
                        "height": capture_region[3]
                    }
                else:
                    monitor = self.sct.monitors[1]  # 主显示器
                
                screenshot = self.sct.grab(monitor)
                img = np.array(screenshot)
                
                # 转换BGRA到BGR
                if len(img.shape) == 3 and img.shape[2] == 4:
                    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                
                return img
                
            elif self.capture_method == 'pyautogui':
                # 使用pyautogui捕获
                import pyautogui
                
                if capture_region:
                    screenshot = self.pyautogui.screenshot(region=capture_region)
                else:
                    screenshot = self.pyautogui.screenshot()
                
                img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                return img
                
            elif self.capture_method == 'dxcam':
                # 使用dxcam捕获
                if capture_region:
                    img = self.camera.grab(region=capture_region)
                else:
                    img = self.camera.grab()
                
                if img is not None:
                    return img
                else:
                    return None
                    
        except Exception as e:
            print(f"屏幕捕获失败: {e}")
            return None
        
        return None
    
    def start_capture(self, fps=10):
        """
        开始连续捕获
        
        参数:
            fps: 帧率
            
        返回:
            生成器，每次yield一帧
        """
        self.capturing = True
        
        while self.capturing:
            start_time = time.time()
            
            # 捕获帧
            frame = self.capture()
            if frame is not None:
                yield frame
            
            # 控制帧率
            elapsed = time.time() - start_time
            if elapsed < 1.0/fps:
                time.sleep(1.0/fps - elapsed)
    
    def stop_capture(self):
        """停止捕获"""
        self.capturing = False
    
    def calibrate_region(self):
        """
        校准屏幕区域
        
        返回:
            校准的区域 (x, y, width, height)
        """
        print("开始屏幕区域校准...")
        print("请用鼠标拖动选择要捕获的屏幕区域")
        
        # 先捕获全屏用于校准
        full_screen = self.capture()
        if full_screen is None:
            print("无法捕获屏幕")
            return None
        
        # 使用OpenCV选择ROI
        roi = cv2.selectROI("屏幕区域校准 - 用鼠标选择区域，按Enter确认", full_screen, False)
        cv2.destroyAllWindows()
        
        if roi[2] > 0 and roi[3] > 0:
            self.region = roi
            print(f"校准完成! 区域: x={roi[0]}, y={roi[1]}, 宽={roi[2]}, 高={roi[3]}")
            
            # 保存校准配置
            self.save_calibration()
            
            return roi
        else:
            print("校准取消")
            return None
    
    def save_calibration(self):
        """保存校准配置"""
        if self.region is None:
            return
        
        import yaml
        config = {
            'screen_capture': {
                'region': {
                    'x': int(self.region[0]),
                    'y': int(self.region[1]),
                    'width': int(self.region[2]),
                    'height': int(self.region[3])
                },
                'method': self.capture_method,
                'calibrated_at': time.strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        
        Path("config").mkdir(exist_ok=True)
        config_file = Path("config/screen_calibration.yaml")
        
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        
        print(f"校准配置已保存: {config_file}")
    
    def load_calibration(self):
        """加载校准配置"""
        config_file = Path("config/screen_calibration.yaml")
        
        if config_file.exists():
            try:
                import yaml
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                
                if 'screen_capture' in config:
                    region_config = config['screen_capture']['region']
                    self.region = (
                        region_config['x'],
                        region_config['y'],
                        region_config['width'],
                        region_config['height']
                    )
                    print(f"加载校准区域: {self.region}")
                    return True
            except Exception as e:
                print(f"加载校准配置失败: {e}")
        
        return False
    
    def preview(self, duration=5):
        """
        预览屏幕捕获
        
        参数:
            duration: 预览时长(秒)
        """
        print(f"屏幕捕获预览 ({duration}秒)...")
        print("按 'q' 可以提前退出预览")
        
        start_time = time.time()
        frame_count = 0
        
        while time.time() - start_time < duration:
            frame = self.capture()
            if frame is None:
                print("无法捕获屏幕")
                break
            
            frame_count += 1
            
            # 显示帧信息
            h, w = frame.shape[:2]
            info_text = f"屏幕捕获: {w}x{h} | 帧: {frame_count}"
            cv2.putText(frame, info_text, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            cv2.imshow('屏幕捕获预览 - 按 q 退出', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cv2.destroyAllWindows()
        print(f"预览结束，共捕获 {frame_count} 帧")

# 测试函数
def test_screen_capture():
    """测试屏幕捕获"""
    print("测试屏幕捕获...")
    
    # 创建屏幕捕获器
    capture = ScreenCapture()
    
    # 获取屏幕尺寸
    screen_size = capture.get_screen_size()
    print(f"屏幕尺寸: {screen_size['width']}x{screen_size['height']}")
    
    # 预览
    capture.preview(duration=3)
    
    # 测试捕获单帧
    print("捕获单帧...")
    frame = capture.capture()
    if frame is not None:
        cv2.imwrite("outputs/screen_capture_test.jpg", frame)
        print(f"捕获帧已保存: outputs/screen_capture_test.jpg")
        print(f"图像尺寸: {frame.shape[1]}x{frame.shape[0]}")
    
    print("屏幕捕获测试完成")

if __name__ == "__main__":
    test_screen_capture()
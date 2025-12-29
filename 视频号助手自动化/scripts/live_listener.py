#!/usr/bin/env python3
"""
live_listener.py - 实时优化版
目标：100-200ms延迟响应
"""

import sys
import json
import os
import time
import threading
import queue
import difflib
from vosk import Model, KaldiRecognizer
import pyaudio
import numpy as np

# ========== 实时配置 ==========
CONFIG_DIR = r"C:\Users\A\Desktop\视频号助手自动化\config"
KEYWORDS_FILE = os.path.join(CONFIG_DIR, "keywords.txt")
MODEL_PATH = "vosk-model-small-cn-0.22"
TRIGGER_FILE = r"C:\Users\A\Desktop\视频号助手自动化\TRIGGER_ME.txt"

# 实时参数
AUDIO_CHUNK_SIZE = 1600  # 减小块大小（原4000）→ 100ms音频
SAMPLE_RATE = 16000
PARTIAL_RESULTS = True   # 启用部分结果
FUZZY_THRESHOLD = 0.65   # 降低阈值，更快触发
MIN_TRIGGER_INTERVAL = 1.0  # 防重复触发间隔

# 默认关键词
DEFAULT_KEYWORDS = ["添加商品", "一百八", "上链接"]
# ==============================

class RealTimeKeywordDetector:
    """实时关键词检测器"""
    
    def __init__(self):
        self.keywords = []
        self.last_trigger_time = 0
        self.load_keywords()
    
    def load_keywords(self):
        """加载关键词"""
        try:
            if os.path.exists(KEYWORDS_FILE):
                with open(KEYWORDS_FILE, 'r', encoding='utf-8') as f:
                    self.keywords = [line.strip() for line in f if line.strip()]
            else:
                self.keywords = DEFAULT_KEYWORDS.copy()
            
            # 按长度排序，短词优先匹配（更快）
            self.keywords.sort(key=len)
            print(f"✅ 加载 {len(self.keywords)} 个关键词: {self.keywords}")
            
        except Exception as e:
            print(f"❌ 加载关键词失败: {e}")
            self.keywords = DEFAULT_KEYWORDS.copy()
    
    def check_trigger_allowed(self):
        """检查是否允许触发（防重复）"""
        current_time = time.time()
        if current_time - self.last_trigger_time < MIN_TRIGGER_INTERVAL:
            return False
        self.last_trigger_time = current_time
        return True
    
    def fast_fuzzy_match(self, text, keyword):
        """快速模糊匹配（优化速度）"""
        if len(keyword) > len(text):
            return False, 0
        
        # 快速相似度计算（简化版）
        for i in range(len(text) - len(keyword) + 1):
            substring = text[i:i+len(keyword)]
            # 简化的相似度计算（比difflib快）
            matches = sum(1 for a, b in zip(substring, keyword) if a == b)
            similarity = matches / len(keyword)
            
            if similarity >= FUZZY_THRESHOLD:
                return True, similarity
        
        return False, 0
    
    def detect(self, text, use_partial=True):
        """
        实时检测关键词
        use_partial: 是否使用部分结果（更快但可能不准）
        """
        if not text:
            return False, None, None
        
        # 1. 精确匹配（最快）
        for keyword in self.keywords:
            if keyword in text:
                return True, keyword, 1.0
        
        # 2. 快速模糊匹配
        if use_partial and len(text) >= 2:
            for keyword in self.keywords:
                if len(keyword) >= 2:  # 只匹配2字以上关键词
                    matched, similarity = self.fast_fuzzy_match(text, keyword)
                    if matched:
                        return True, keyword, similarity
        
        return False, None, None

class AudioProcessor(threading.Thread):
    """音频处理线程（实时）"""
    
    def __init__(self, detector):
        super().__init__()
        self.detector = detector
        self.running = True
        self.audio_queue = queue.Queue(maxsize=10)
        
        # 初始化音频
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.model = Model(MODEL_PATH)
        self.recognizer = KaldiRecognizer(self.model, SAMPLE_RATE)
        
        # 启用部分结果（关键！）
        self.recognizer.SetPartialWords(PARTIAL_RESULTS)
        
        # 性能监控
        self.processing_times = []
    
    def start_capture(self):
        """开始音频捕获"""
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=AUDIO_CHUNK_SIZE,
            stream_callback=self.audio_callback
        )
        self.stream.start_stream()
    
    def audio_callback(self, in_data, frame_count, time_info, status):
        """音频回调函数（实时）"""
        self.audio_queue.put(in_data)
        return (in_data, pyaudio.paContinue)
    
    def process_audio_chunk(self, data):
        """处理音频块（核心）"""
        start_time = time.time()
        
        # 1. 语音识别
        if self.recognizer.AcceptWaveform(data):
            # 完整结果
            result = json.loads(self.recognizer.Result())
            text = result.get("text", "").strip()
            result_type = "完整"
        else:
            # 部分结果（更快！）
            partial = json.loads(self.recognizer.PartialResult())
            text = partial.get("partial", "").strip()
            result_type = "部分"
        
        # 2. 关键词检测
        if text:
            # 部分结果用模糊匹配，完整结果用精确匹配
            use_fuzzy = (result_type == "部分")
            detected, keyword, similarity = self.detector.detect(text, use_fuzzy)
            
            if detected:
                # 检查防重复
                if not self.detector.check_trigger_allowed():
                    return
                
                # 触发点击
                print(f"⚡ [{result_type}] 触发: '{keyword}' ({similarity:.2f})")
                print(f"   📝 文本: '{text}'")
                self.trigger_click()
        
        # 性能记录
        process_time = (time.time() - start_time) * 1000  # 毫秒
        self.processing_times.append(process_time)
        
        # 每100次输出一次平均处理时间
        if len(self.processing_times) % 100 == 0:
            avg_time = np.mean(self.processing_times[-100:])
            print(f"📊 平均处理时间: {avg_time:.1f}ms")
    
    def trigger_click(self):
        """触发点击（异步）"""
        def create_trigger():
            try:
                with open(TRIGGER_FILE, 'w') as f:
                    f.write('')
                # 快速清理（不等待1秒了）
                time.sleep(0.2)
                if os.path.exists(TRIGGER_FILE):
                    os.remove(TRIGGER_FILE)
            except Exception as e:
                print(f"❌ 触发失败: {e}")
        
        # 异步执行，不阻塞音频处理
        threading.Thread(target=create_trigger, daemon=True).start()
    
    def run(self):
        """主处理循环"""
        self.start_capture()
        print(f"✅ 音频捕获启动 (块大小: {AUDIO_CHUNK_SIZE})")
        
        try:
            while self.running:
                try:
                    # 获取音频数据（非阻塞）
                    data = self.audio_queue.get(timeout=0.1)
                    self.process_audio_chunk(data)
                except queue.Empty:
                    continue
                    
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()
    
    def stop(self):
        """停止处理"""
        self.running = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.audio.terminate()
        print("🔧 音频资源已释放")

def main():
    """主函数"""
    print("=" * 60)
    print("⚡ 实时语音触发系统")
    print("=" * 60)
    print(f"🎯 目标延迟: 100-200ms")
    print(f"📁 音频块大小: {AUDIO_CHUNK_SIZE} samples ({AUDIO_CHUNK_SIZE/16}ms)")
    print(f"🔧 部分结果: {'启用' if PARTIAL_RESULTS else '禁用'}")
    print(f"🎤 采样率: {SAMPLE_RATE}Hz")
    print("=" * 60)
    
    # 初始化检测器
    detector = RealTimeKeywordDetector()
    
    # 启动音频处理器
    processor = AudioProcessor(detector)
    processor.start()
    
    try:
        # 主线程等待
        while processor.is_alive():
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n⏹️ 停止系统...")
        processor.stop()
    
    processor.join()
    
    # 输出性能报告
    if processor.processing_times:
        avg_time = np.mean(processor.processing_times)
        max_time = np.max(processor.processing_times)
        min_time = np.min(processor.processing_times)
        print(f"\n📊 性能报告:")
        print(f"   平均处理时间: {avg_time:.1f}ms")
        print(f"   最快: {min_time:.1f}ms")
        print(f"   最慢: {max_time:.1f}ms")
        print(f"   总处理次数: {len(processor.processing_times)}")

if __name__ == '__main__':
    main()
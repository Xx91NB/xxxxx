import pyaudio
import time

print("=" * 50)
print("音频设备配置测试")
print("=" * 50)

p = pyaudio.PyAudio()

print("\n1. 可用的音频输入设备：")
cable_found = False
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    if info['maxInputChannels'] > 0:  # 输入设备
        device_name = info['name']
        print(f"   [{i}] {device_name}")
        if 'CABLE' in device_name.upper():
            cable_found = True
            print(f"      ← 找到虚拟音频设备！")

print("\n2. 测试录音...")
if cable_found:
    # 尝试从第一个输入设备录音
    try:
        stream = p.open(format=pyaudio.paInt16,
                       channels=1,
                       rate=16000,
                       input=True,
                       frames_per_buffer=1024)
        
        print("正在监听音频（说几句话试试）...")
        for i in range(5):
            data = stream.read(1024)
            volume = max(data) if data else 0
            print(f"  第{i+1}秒: {'有声音' if volume > 10 else '无声音'}")
            time.sleep(1)
        
        stream.stop_stream()
        stream.close()
        print("\n✅ 音频设备工作正常！")
        
    except Exception as e:
        print(f"\n❌ 录音失败: {e}")
        print("请检查：")
        print("  1. VB-Cable是否安装成功")
        print("  2. 声音设置中CABLE Output是否设为默认")
        print("  3. 系统音量是否开启")
else:
    print("\n❌ 未找到虚拟音频设备")
    print("请先安装VB-Cable并正确配置")

p.terminate()
print("\n" + "=" * 50)
input("按Enter键退出...")
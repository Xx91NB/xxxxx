\# 直播商品识别系统 4.0



基于计算机视觉的智能商品识别系统，支持实时视频流和图像的商品检测与识别。



\## 功能特性



\- 🎯 \*\*多模式识别\*\*：支持图像、视频、混合模式

\- 📷 \*\*实时处理\*\*：摄像头实时视频流处理

\- 🔍 \*\*智能匹配\*\*：基于特征点的智能匹配算法

\- 📊 \*\*数据统计\*\*：完整的处理统计和报告

\- 🧠 \*\*学习功能\*\*：系统可学习新商品

\- 🎨 \*\*友好界面\*\*：直观的可视化界面



\## 系统要求



\- Python 3.8+

\- Windows/Linux/macOS

\- 摄像头（可选）

\- 2GB+ RAM



\## 安装步骤



1\. 克隆或下载本项目

2\. 安装依赖：
pip install -r requirements.txt
text

3\. 准备素材：

\- 将商品图片放入 `data/images\_material/`

\- 将商品视频放入 `data/videos\_material/`



\## 使用方法



\### 快速启动
python start.py
text



\### 命令行启动
主程序

python main.py



屏幕校准

python calibrate\_region.py



素材检查

python check\_materials.py
text



\### 高级使用
使用智能系统

python -c "from core.intelligent\_system import IntelligentSystem; system = IntelligentSystem(); system.run\_with\_gui(0)"
图像匹配测试

python -c "from image\_matcher import ImageMatcher; matcher = ImageMatcher(); matcher.load\_templates\_from\_dir('data/images\_material')"



text



\## 项目结构

直播商品识别系统4.0/

├── start.py # 启动器

├── main.py # 主程序

├── requirements.txt # 依赖包

├── config/ # 配置文件

├── core/ # 核心代码

├── data/ # 数据目录

├── outputs/ # 输出目录

├── tools/ # 工具脚本

└── README.md # 说明文档
text



\## 配置文件



系统支持多种配置文件：

\- `config/default.yaml` - 默认配置

\- `config/hybrid\_mode.yaml` - 混合模式

\- `config/image\_mode.yaml` - 图像模式

\- `config/video\_mode.yaml` - 视频模式



\## 快捷键



\- \*\*q\*\* - 退出程序

\- \*\*s\*\* - 保存截图

\- \*\*l\*\* - 学习当前商品

\- \*\*1\*\* - 图像模式

\- \*\*2\*\* - 视频模式

\- \*\*3\*\* - 混合模式



\## 常见问题



\### 1. 摄像头无法打开

\- 检查摄像头是否正确连接

\- 尝试不同的摄像头ID（0, 1, 2...）



\### 2. 匹配效果不佳

\- 确保模板图片清晰

\- 调整匹配参数（min\_matches, match\_ratio）

\- 增加更多角度的模板图片



\### 3. 程序运行缓慢

\- 降低视频分辨率

\- 增加frame\_interval参数

\- 关闭不必要的功能



\## 许可证



MIT License



# KJZ 红外图像查看器

一个用于查看和处理 `.datx` 格式红外图像的 Python GUI 应用程序。

![应用截图](docs/screenshot.png)
*（待添加实际截图）*

## 项目简介

本项目是一个专门用于处理红外图像数据的查看器，支持读取 `.datx` 格式的 14-bit 红外图像文件（640×512 分辨率），并提供丰富的图像处理功能。

## 功能特性

### 📁 文件操作
- ✅ 打开 `.datx` 格式红外图像文件
- ✅ 支持多帧数据加载
- ✅ 保存处理后的图像为 PNG/TIFF 格式

### 🎞️ 帧浏览
- ✅ 滑动条拖动浏览多帧数据
- ✅ 显示当前帧号和总帧数

### 🎨 显示设置
- ✅ **位数切换**：支持 14-bit 原始显示和 8-bit 映射显示
- ✅ **自动对比度**：动态范围拉伸增强图像对比度
- ✅ **伪彩色映射**：提供多种色彩映射方案
  - 灰度（默认）
  - Jet
  - Hot
  - Inferno
  - Viridis
  - Turbo
  - Rainbow
  - Ocean
  - Parula

### 🔍 空域滤波
- ✅ **高斯滤波**：可调节核大小（3-15）
- ✅ **中值滤波**：可调节核大小（3-15）
- ✅ **双边滤波**：保边平滑处理

### ⏱️ 时域滤波
- ✅ **多帧滑动平均**：可调节窗口大小（3-21）

### 🖼️ 背景处理
- ✅ 设置当前帧为背景帧
- ✅ 背景减除操作
- ✅ 清除背景

## 技术规格

- **图像格式**：640×512，14-bit 红外图像
- **数据格式**：`.datx` 二进制文件（小端序 uint16）
- **GUI 框架**：PyQt5
- **图像处理**：OpenCV + NumPy + SciPy

## 环境配置

### 使用 Conda（推荐）

```bash
# 创建并激活环境
conda env create -f environment.yml
conda activate kjzviewer
```

### 使用 pip

```bash
# 创建虚拟环境（可选）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

## 运行方法

```bash
# 确保已激活环境
python main.py
```

## 使用说明

### 基本操作流程

1. **打开文件**
   - 点击"打开 DatX 文件"按钮
   - 选择 `.datx` 格式的红外图像文件
   - 文件加载后会显示第一帧图像

2. **浏览帧**
   - 使用底部的滑动条切换不同帧
   - 帧号显示在滑动条右侧

3. **调整显示**
   - 选择 8-bit 或 14-bit 显示模式
   - 勾选"自动对比度"增强图像
   - 从下拉菜单选择伪彩色映射方案

4. **应用滤波**
   - 勾选相应的滤波器复选框
   - 调整滤波参数（核大小、窗口大小等）
   - 图像会实时更新

5. **背景处理**
   - 切换到某一帧作为背景帧
   - 点击"设置当前帧为背景"
   - 勾选"减背景"进行背景减除
   - 需要时可以"清除背景"

6. **保存图像**
   - 点击"保存当前帧"按钮
   - 选择保存位置和格式（PNG/TIFF）
   - 保存的是经过所有处理后的图像

### 滤波器说明

- **高斯滤波**：平滑图像，减少噪声，适合去除高斯噪声
- **中值滤波**：去除椒盐噪声，保持边缘
- **双边滤波**：在平滑的同时保持边缘细节
- **多帧平均**：利用时域信息降噪，需要多帧数据

### 注意事项

- `.datx` 文件必须符合 640×512 分辨率规格
- 数据存储格式为小端序 uint16
- 14-bit 数据使用掩码 `0x3FFF` 提取有效位
- 多帧平均需要至少 3 帧数据
- 处理大文件时可能需要一定时间

## 项目结构

```
KJZViewer/
├── main.py                    # 程序入口
├── requirements.txt           # pip 依赖列表
├── environment.yml            # conda 环境配置
├── README.md                  # 本文件
├── core/                      # 核心处理模块
│   ├── __init__.py
│   ├── datx_reader.py         # datx 文件读取
│   ├── image_processor.py     # 图像处理管线
│   └── filters.py             # 滤波器集合
├── gui/                       # 界面模块
│   ├── __init__.py
│   ├── main_window.py         # 主窗口
│   └── resources/             # 资源文件夹
│       └── .gitkeep
└── utils/                     # 工具函数
    ├── __init__.py
    └── colormap.py            # 伪彩映射工具
```

## 开发说明

### 核心模块

- `DatxReader`: 负责读取和解析 `.datx` 文件
- `ImageProcessor`: 集成图像处理管线
- `ImageFilters`: 提供各种滤波算法
- `ColormapConverter`: 伪彩色映射转换

### 扩展功能

可以通过以下方式扩展：
- 添加新的滤波算法到 `filters.py`
- 添加新的色彩映射到 `colormap.py`
- 在 `main_window.py` 中添加新的 UI 控件

## 许可证

请参阅 [LICENSE](LICENSE) 文件。

## 联系方式

如有问题或建议，请提交 Issue 或 Pull Request。

---

**注意**：本项目专门设计用于处理特定格式的红外图像数据，如需处理其他格式，请根据实际需求修改 `datx_reader.py` 中的读取逻辑。

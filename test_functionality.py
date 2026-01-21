#!/usr/bin/env python3
"""
测试脚本：验证红外图像处理功能
"""
import sys
sys.path.insert(0, '.')

import numpy as np
from core.datx_reader import DatxReader
from core.image_processor import ImageProcessor
from core.filters import ImageFilters
from utils.colormap import ColormapConverter


def create_test_file(filename='/tmp/test_data/test_thermal.datx'):
    """创建测试用的 datx 文件"""
    print("创建测试数据文件...")
    
    width, height, n_frames = 640, 512, 5
    frames = []
    
    for i in range(n_frames):
        x = np.linspace(0, 10, width)
        y = np.linspace(0, 10, height)
        X, Y = np.meshgrid(x, y)
        
        center_x, center_y = 5 + i * 0.1, 5 + i * 0.1
        dist = np.sqrt((X - center_x)**2 + (Y - center_y)**2)
        thermal = 5000 + 3000 * np.exp(-dist**2 / 5)
        
        noise = np.random.randint(-200, 200, size=(height, width))
        frame = np.clip(thermal + noise, 0, 16383).astype(np.uint16)
        frames.append(frame)
    
    all_frames = np.stack(frames)
    
    import os
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'wb') as f:
        all_frames.astype('<u2').tofile(f)
    
    print(f"✓ 创建测试文件: {filename}")
    print(f"  - 帧数: {n_frames}")
    print(f"  - 尺寸: {width}×{height}")
    print(f"  - 数据范围: {all_frames.min()} - {all_frames.max()}")
    return filename


def test_datx_reader(filename):
    """测试 DatX 读取器"""
    print("\n测试 DatxReader...")
    
    reader = DatxReader()
    frames = reader.load(filename)
    
    print(f"✓ 成功加载 {reader.get_frame_count()} 帧")
    print(f"  - 帧形状: {frames.shape}")
    print(f"  - 数据类型: {frames.dtype}")
    print(f"  - 值范围: {frames.min()} - {frames.max()}")
    
    # 测试单帧获取
    frame0 = reader.get_frame(0)
    print(f"✓ 获取单帧成功, 形状: {frame0.shape}")
    
    return reader, frames


def test_filters(frames):
    """测试滤波器"""
    print("\n测试滤波器...")
    
    frame0 = frames[0].astype(np.float32)
    
    # 高斯滤波
    gaussian = ImageFilters.gaussian_blur(frame0, kernel_size=5)
    print(f"✓ 高斯滤波: {gaussian.shape}")
    
    # 中值滤波
    median = ImageFilters.median_filter(frames[0], kernel_size=3)
    print(f"✓ 中值滤波: {median.shape}")
    
    # 双边滤波
    bilateral = ImageFilters.bilateral_filter(frame0, d=9)
    print(f"✓ 双边滤波: {bilateral.shape}")
    
    # 时域平均
    temporal = ImageFilters.temporal_average(frames, current_idx=2, window=3)
    print(f"✓ 时域平均: {temporal.shape}")
    
    # 背景减除
    background = frames[0].astype(np.float32)
    subtracted = ImageFilters.subtract_background(frame0, background)
    print(f"✓ 背景减除: {subtracted.shape}")


def test_image_processor(frames):
    """测试图像处理器"""
    print("\n测试 ImageProcessor...")
    
    processor = ImageProcessor()
    frame0 = frames[0]
    
    # 测试 8-bit 转换
    processor.bit_mode = 8
    processed_8bit = processor.process(frame0)
    print(f"✓ 8-bit 处理: {processed_8bit.shape}, dtype={processed_8bit.dtype}")
    print(f"  - 值范围: {processed_8bit.min()} - {processed_8bit.max()}")
    
    # 测试 14-bit 处理
    processor.bit_mode = 14
    processed_14bit = processor.process(frame0)
    print(f"✓ 14-bit 处理: {processed_14bit.shape}, dtype={processed_14bit.dtype}")
    
    # 测试自动对比度
    processor.enable_auto_contrast = True
    processed_contrast = processor.process(frame0)
    print(f"✓ 自动对比度: 已启用")
    
    # 测试组合滤波
    processor.enable_gaussian = True
    processor.gaussian_kernel = 5
    processor.enable_temporal = True
    processor.temporal_window = 3
    processed_combined = processor.process(frame0, all_frames=frames, frame_idx=1)
    print(f"✓ 组合处理: {processed_combined.shape}")
    
    return processor


def test_colormap(image):
    """测试伪彩色映射"""
    print("\n测试 ColormapConverter...")
    
    converter = ColormapConverter()
    colormaps = converter.get_available_colormaps()
    print(f"✓ 可用色彩映射: {len(colormaps)} 种")
    
    for cmap_name in ['灰度', 'Jet', 'Hot', 'Inferno']:
        colored = converter.apply_colormap(image, cmap_name)
        print(f"  - {cmap_name}: {colored.shape}")
    
    print("✓ 所有色彩映射测试通过")


def test_complete_pipeline(frames):
    """测试完整处理管线"""
    print("\n测试完整处理管线...")
    
    processor = ImageProcessor()
    converter = ColormapConverter()
    
    # 设置背景
    background_frame = frames[0]
    processor.set_background(background_frame)
    print("✓ 已设置背景帧")
    
    # 配置处理参数
    processor.bit_mode = 8
    processor.enable_auto_contrast = True
    processor.enable_gaussian = True
    processor.gaussian_kernel = 5
    processor.enable_background_subtraction = True
    
    # 处理一帧
    current_frame = frames[2]
    processed = processor.process(current_frame, all_frames=frames, frame_idx=2)
    print(f"✓ 图像处理完成: {processed.shape}")
    
    # 应用伪彩色
    colored = converter.apply_colormap(processed, 'Jet')
    print(f"✓ 伪彩色映射完成: {colored.shape}")
    
    # 模拟保存
    import cv2
    output_file = '/tmp/test_output.png'
    cv2.imwrite(output_file, cv2.cvtColor(colored, cv2.COLOR_RGB2BGR))
    print(f"✓ 图像已保存: {output_file}")


def main():
    """主测试函数"""
    print("=" * 60)
    print("KJZ 红外图像查看器 - 功能测试")
    print("=" * 60)
    
    try:
        # 创建测试文件
        test_file = create_test_file()
        
        # 测试读取器
        reader, frames = test_datx_reader(test_file)
        
        # 测试滤波器
        test_filters(frames)
        
        # 测试图像处理器
        processor = test_image_processor(frames)
        
        # 测试伪彩色映射
        test_image = processor.process(frames[0])
        test_colormap(test_image)
        
        # 测试完整管线
        test_complete_pipeline(frames)
        
        print("\n" + "=" * 60)
        print("✓ 所有测试通过！")
        print("=" * 60)
        print("\n要启动 GUI 界面，请运行：")
        print("  python main.py")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

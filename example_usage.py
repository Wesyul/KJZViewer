#!/usr/bin/env python3
"""
示例：程序化使用图像处理功能
演示如何不使用 GUI 直接处理 datx 文件
"""
import sys
sys.path.insert(0, '.')

import numpy as np
import cv2
from pathlib import Path

from core.datx_reader import DatxReader
from core.image_processor import ImageProcessor
from utils.colormap import ColormapConverter


def process_datx_file(input_file, output_dir=None):
    """
    处理 datx 文件并保存结果
    
    参数:
        input_file: 输入的 datx 文件路径
        output_dir: 输出目录（默认为输入文件同级目录）
    """
    # 创建输出目录
    if output_dir is None:
        output_dir = Path(input_file).parent / "processed"
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(exist_ok=True)
    
    print(f"处理文件: {input_file}")
    print(f"输出目录: {output_dir}")
    print("-" * 60)
    
    # 加载数据
    reader = DatxReader()
    frames = reader.load(input_file)
    print(f"加载了 {reader.get_frame_count()} 帧")
    
    # 初始化处理器
    processor = ImageProcessor()
    processor.bit_mode = 8
    processor.enable_auto_contrast = True
    processor.enable_gaussian = True
    processor.gaussian_kernel = 5
    
    # 初始化伪彩色转换器
    converter = ColormapConverter()
    
    # 设置第一帧为背景
    background = reader.get_frame(0)
    processor.set_background(background)
    
    # 处理所有帧
    for idx in range(reader.get_frame_count()):
        print(f"处理帧 {idx + 1}/{reader.get_frame_count()}...", end=" ")
        
        # 获取原始帧
        raw_frame = reader.get_frame(idx)
        
        # 处理图像
        processed = processor.process(raw_frame, all_frames=frames, frame_idx=idx)
        
        # 应用伪彩色映射
        colored_jet = converter.apply_colormap(processed, 'Jet')
        colored_hot = converter.apply_colormap(processed, 'Hot')
        colored_inferno = converter.apply_colormap(processed, 'Inferno')
        
        # 保存结果
        base_name = f"frame_{idx:04d}"
        
        # 保存灰度图
        cv2.imwrite(str(output_dir / f"{base_name}_gray.png"), processed)
        
        # 保存伪彩色图
        cv2.imwrite(str(output_dir / f"{base_name}_jet.png"), 
                   cv2.cvtColor(colored_jet, cv2.COLOR_RGB2BGR))
        cv2.imwrite(str(output_dir / f"{base_name}_hot.png"), 
                   cv2.cvtColor(colored_hot, cv2.COLOR_RGB2BGR))
        cv2.imwrite(str(output_dir / f"{base_name}_inferno.png"), 
                   cv2.cvtColor(colored_inferno, cv2.COLOR_RGB2BGR))
        
        print("✓")
    
    print("-" * 60)
    print(f"处理完成！结果保存在: {output_dir}")
    
    return output_dir


def main():
    """主函数"""
    # 示例：创建测试数据并处理
    print("KJZ 红外图像处理器 - 编程示例")
    print("=" * 60)
    
    # 创建测试数据
    print("\n1. 创建测试数据...")
    test_file = "/tmp/test_data/example.datx"
    
    # 创建简单的测试数据
    width, height, n_frames = 640, 512, 3
    frames = []
    
    for i in range(n_frames):
        # 创建渐变热斑
        x = np.linspace(0, 10, width)
        y = np.linspace(0, 10, height)
        X, Y = np.meshgrid(x, y)
        
        # 移动的热点
        cx, cy = 5 + i, 5
        dist = np.sqrt((X - cx)**2 + (Y - cy)**2)
        thermal = 6000 + 2000 * np.exp(-dist**2 / 3)
        
        # 添加噪声
        noise = np.random.randint(-100, 100, size=(height, width))
        frame = np.clip(thermal + noise, 0, 16383).astype(np.uint16)
        frames.append(frame)
    
    all_frames = np.stack(frames)
    
    import os
    os.makedirs(os.path.dirname(test_file), exist_ok=True)
    with open(test_file, 'wb') as f:
        all_frames.astype('<u2').tofile(f)
    
    print(f"✓ 创建了 {n_frames} 帧测试数据")
    
    # 处理文件
    print("\n2. 处理图像...")
    output_dir = process_datx_file(test_file, "/tmp/test_data/output")
    
    # 显示结果
    print("\n3. 生成的文件:")
    for file_path in sorted(output_dir.glob("*.png")):
        print(f"  - {file_path.name}")
    
    print("\n=" * 60)
    print("示例运行完成！")
    print("\n提示：")
    print("  - 查看生成的图像: ls /tmp/test_data/output/")
    print("  - 启动 GUI 界面: python main.py")


if __name__ == "__main__":
    main()

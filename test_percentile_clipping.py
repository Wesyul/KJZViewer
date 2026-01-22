#!/usr/bin/env python3
"""
测试百分比裁剪功能
测试图像显示的百分比裁剪和实际最大最小值归一化
"""
import sys
sys.path.insert(0, '.')

import numpy as np
from core.image_processor import ImageProcessor


def create_test_image_with_outliers(height=100, width=100):
    """
    创建带有异常值的测试图像
    
    返回:
        image: 测试图像，包含少量极端亮点和暗点
    """
    # 创建基础图像：范围 5000-5500（动态范围很小）
    image = np.random.uniform(5000, 5500, size=(height, width)).astype(np.float32)
    
    # 添加少量极端亮点（模拟噪声）
    n_bright = 20
    bright_coords = [np.random.randint(0, height, n_bright),
                     np.random.randint(0, width, n_bright)]
    image[bright_coords] = 15000  # 极亮的点
    
    # 添加少量极端暗点
    n_dark = 20
    dark_coords = [np.random.randint(0, height, n_dark),
                   np.random.randint(0, width, n_dark)]
    image[dark_coords] = 100  # 极暗的点
    
    return image


def test_basic_normalization():
    """测试基础归一化（使用实际最大最小值）"""
    print("\n测试基础归一化（实际最大最小值）...")
    
    image = create_test_image_with_outliers()
    processor = ImageProcessor()
    
    # 8-bit 模式，不使用百分比裁剪
    processor.bit_mode = 8
    processor.enable_percentile_clipping = False
    
    result = processor.convert_display_bits(image)
    
    print(f"✓ 基础归一化完成")
    print(f"  - 输入范围: {image.min():.1f} - {image.max():.1f}")
    print(f"  - 输出范围: {result.min()} - {result.max()}")
    print(f"  - 输出类型: {result.dtype}")
    
    # 验证
    assert result.dtype == np.uint8, "8-bit 模式输出应为 uint8"
    assert result.min() >= 0 and result.max() <= 255, "8-bit 输出应在 0-255 范围内"
    
    # 由于有极端值，输出应该接近 0-255 的完整范围
    assert result.max() > 200, "应该使用完整输出范围"
    
    print("✓ 基础归一化测试通过")


def test_percentile_clipping_8bit():
    """测试 8-bit 百分比裁剪"""
    print("\n测试 8-bit 百分比裁剪...")
    
    image = create_test_image_with_outliers()
    processor = ImageProcessor()
    
    # 8-bit 模式，使用百分比裁剪
    processor.bit_mode = 8
    processor.enable_percentile_clipping = True
    processor.low_percentile = 1.0
    processor.high_percentile = 99.0
    
    result = processor.convert_display_bits(image)
    
    print(f"✓ 百分比裁剪完成")
    print(f"  - 输入范围: {image.min():.1f} - {image.max():.1f}")
    print(f"  - 1% 百分位: {np.percentile(image, 1.0):.1f}")
    print(f"  - 99% 百分位: {np.percentile(image, 99.0):.1f}")
    print(f"  - 输出范围: {result.min()} - {result.max()}")
    print(f"  - 输出类型: {result.dtype}")
    
    # 验证
    assert result.dtype == np.uint8, "8-bit 模式输出应为 uint8"
    assert result.min() >= 0 and result.max() <= 255, "8-bit 输出应在 0-255 范围内"
    
    # 使用百分比裁剪后，应该更好地利用动态范围
    assert result.max() > 200, "应该使用完整输出范围"
    
    print("✓ 8-bit 百分比裁剪测试通过")


def test_percentile_clipping_14bit():
    """测试 14-bit 百分比裁剪"""
    print("\n测试 14-bit 百分比裁剪...")
    
    image = create_test_image_with_outliers()
    processor = ImageProcessor()
    
    # 14-bit 模式，使用百分比裁剪
    processor.bit_mode = 14
    processor.enable_percentile_clipping = True
    processor.low_percentile = 2.0
    processor.high_percentile = 98.0
    
    result = processor.convert_display_bits(image)
    
    print(f"✓ 14-bit 百分比裁剪完成")
    print(f"  - 输入范围: {image.min():.1f} - {image.max():.1f}")
    print(f"  - 2% 百分位: {np.percentile(image, 2.0):.1f}")
    print(f"  - 98% 百分位: {np.percentile(image, 98.0):.1f}")
    print(f"  - 输出范围: {result.min()} - {result.max()}")
    print(f"  - 输出类型: {result.dtype}")
    
    # 验证
    assert result.dtype == np.uint16, "14-bit 模式输出应为 uint16"
    assert result.min() >= 0 and result.max() <= 16383, "14-bit 输出应在 0-16383 范围内"
    
    print("✓ 14-bit 百分比裁剪测试通过")


def test_small_dynamic_range():
    """测试小动态范围图像（主要问题场景）"""
    print("\n测试小动态范围图像...")
    
    # 创建动态范围很小的图像（5000-5100）
    image = np.random.uniform(5000, 5100, size=(100, 100)).astype(np.float32)
    processor = ImageProcessor()
    
    # 不使用百分比裁剪
    processor.bit_mode = 8
    processor.enable_percentile_clipping = False
    result1 = processor.convert_display_bits(image)
    
    print(f"✓ 小动态范围测试")
    print(f"  - 输入范围: {image.min():.1f} - {image.max():.1f}")
    print(f"  - 输出范围（实际值归一化）: {result1.min()} - {result1.max()}")
    
    # 验证：即使动态范围小，也应该使用完整输出范围
    assert result1.max() > 200, "小动态范围图像应该被拉伸到完整范围"
    assert result1.max() - result1.min() > 200, "应该使用大部分输出范围"
    
    print("✓ 小动态范围测试通过 - 图像应该清晰可见")


def test_uniform_image():
    """测试均匀图像（边界情况）"""
    print("\n测试均匀图像...")
    
    # 创建完全均匀的图像
    image = np.full((100, 100), 5000.0, dtype=np.float32)
    processor = ImageProcessor()
    
    processor.bit_mode = 8
    processor.enable_percentile_clipping = False
    result = processor.convert_display_bits(image)
    
    print(f"✓ 均匀图像测试")
    print(f"  - 输入值: {image[0, 0]:.1f} (所有像素相同)")
    print(f"  - 输出值: {result[0, 0]} (所有像素相同)")
    
    # 验证：所有像素应该相同
    assert np.all(result == result[0, 0]), "均匀图像输出应该保持均匀"
    
    print("✓ 均匀图像测试通过")


def test_different_percentiles():
    """测试不同的百分比参数"""
    print("\n测试不同的百分比参数...")
    
    image = create_test_image_with_outliers()
    processor = ImageProcessor()
    processor.bit_mode = 8
    processor.enable_percentile_clipping = True
    
    # 测试不同的百分比范围
    percentile_configs = [
        (0.5, 99.5),
        (1.0, 99.0),
        (2.0, 98.0),
        (5.0, 95.0),
    ]
    
    for low, high in percentile_configs:
        processor.low_percentile = low
        processor.high_percentile = high
        result = processor.convert_display_bits(image)
        
        print(f"  - 百分比 {low}%-{high}%: 输出范围 {result.min()}-{result.max()}")
        
        assert result.dtype == np.uint8, "输出应为 uint8"
        assert result.min() >= 0 and result.max() <= 255, "输出应在有效范围内"
    
    print("✓ 不同百分比参数测试通过")


def main():
    """主测试函数"""
    print("=" * 60)
    print("测试百分比裁剪功能")
    print("=" * 60)
    
    try:
        test_basic_normalization()
        test_percentile_clipping_8bit()
        test_percentile_clipping_14bit()
        test_small_dynamic_range()
        test_uniform_image()
        test_different_percentiles()
        
        print("\n" + "=" * 60)
        print("✓ 所有百分比裁剪测试通过！")
        print("=" * 60)
        print("\n关键改进：")
        print("1. ✓ 使用实际最大最小值归一化（而不是固定的 16383）")
        print("2. ✓ 小动态范围图像现在可以清晰显示")
        print("3. ✓ 百分比裁剪可以排除异常噪点")
        print("4. ✓ 支持 8-bit 和 14-bit 两种模式")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

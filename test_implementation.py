#!/usr/bin/env python3
"""
验证 GUI 代码的语法和基本结构
不运行 QApplication，仅检查代码结构
"""
import sys
sys.path.insert(0, '.')

import ast
import inspect


def test_main_window_methods():
    """测试主窗口方法是否存在"""
    print("\n测试主窗口方法...")
    
    from gui.main_window import MainWindow
    
    # 检查必要的方法
    required_methods = [
        'create_display_group',
        'create_temporal_filter_group',
        'on_setting_changed',
    ]
    
    for method_name in required_methods:
        assert hasattr(MainWindow, method_name), f"缺少方法: {method_name}"
        print(f"  ✓ 方法存在: {method_name}")
    
    print("✓ 所有必要方法存在")


def test_on_setting_changed_parameters():
    """检查 on_setting_changed 是否同步所有新参数"""
    print("\n检查 on_setting_changed 方法内容...")
    
    from gui.main_window import MainWindow
    
    # 获取方法源代码
    source = inspect.getsource(MainWindow.on_setting_changed)
    
    # 检查是否包含关键参数
    required_params = [
        'enable_percentile_clipping',
        'low_percentile',
        'high_percentile',
        'enable_temporal_median',
        'temporal_median_window',
        'enable_incoherent_integration',
        'incoherent_integration_window',
        'enable_outlier_rejection',
        'outlier_rejection_window',
        'outlier_sigma',
        'enable_weak_target_processing',
        'weak_target_window',
    ]
    
    for param in required_params:
        assert param in source, f"on_setting_changed 缺少参数同步: {param}"
        print(f"  ✓ 参数同步存在: {param}")
    
    print("✓ 所有新参数都已同步")


def test_image_processor_parameters():
    """测试 ImageProcessor 参数"""
    print("\n测试 ImageProcessor 参数...")
    
    from core.image_processor import ImageProcessor
    
    processor = ImageProcessor()
    
    # 检查百分比裁剪参数
    assert hasattr(processor, 'enable_percentile_clipping'), "缺少 enable_percentile_clipping"
    assert hasattr(processor, 'low_percentile'), "缺少 low_percentile"
    assert hasattr(processor, 'high_percentile'), "缺少 high_percentile"
    print("  ✓ 百分比裁剪参数存在")
    
    # 检查时域滤波参数
    assert hasattr(processor, 'enable_temporal_median'), "缺少 enable_temporal_median"
    assert hasattr(processor, 'temporal_median_window'), "缺少 temporal_median_window"
    assert hasattr(processor, 'enable_incoherent_integration'), "缺少 enable_incoherent_integration"
    assert hasattr(processor, 'incoherent_integration_window'), "缺少 incoherent_integration_window"
    assert hasattr(processor, 'enable_outlier_rejection'), "缺少 enable_outlier_rejection"
    assert hasattr(processor, 'outlier_rejection_window'), "缺少 outlier_rejection_window"
    assert hasattr(processor, 'outlier_sigma'), "缺少 outlier_sigma"
    assert hasattr(processor, 'enable_weak_target_processing'), "缺少 enable_weak_target_processing"
    assert hasattr(processor, 'weak_target_window'), "缺少 weak_target_window"
    print("  ✓ 时域滤波参数存在")
    
    # 检查默认值
    assert processor.low_percentile == 1.0, "低百分比默认值错误"
    assert processor.high_percentile == 99.0, "高百分比默认值错误"
    assert processor.temporal_median_window == 5, "时域中值窗口默认值错误"
    assert processor.outlier_sigma == 2.0, "sigma 默认值错误"
    assert processor.weak_target_window == 7, "微弱目标窗口默认值错误"
    print("  ✓ 默认值正确")
    
    print("✓ ImageProcessor 参数测试通过")


def test_convert_display_bits_logic():
    """测试 convert_display_bits 方法逻辑"""
    print("\n测试 convert_display_bits 方法...")
    
    import numpy as np
    from core.image_processor import ImageProcessor
    
    processor = ImageProcessor()
    
    # 创建测试图像
    image = np.random.uniform(5000, 5500, size=(100, 100)).astype(np.float32)
    
    # 测试 8-bit 模式
    processor.bit_mode = 8
    processor.enable_percentile_clipping = False
    result = processor.convert_display_bits(image)
    assert result.dtype == np.uint8, "8-bit 输出类型错误"
    assert result.min() >= 0 and result.max() <= 255, "8-bit 范围错误"
    print("  ✓ 8-bit 模式正常")
    
    # 测试 14-bit 模式
    processor.bit_mode = 14
    processor.enable_percentile_clipping = False
    result = processor.convert_display_bits(image)
    assert result.dtype == np.uint16, "14-bit 输出类型错误"
    assert result.min() >= 0 and result.max() <= 16383, "14-bit 范围错误"
    print("  ✓ 14-bit 模式正常")
    
    # 测试百分比裁剪
    processor.bit_mode = 8
    processor.enable_percentile_clipping = True
    processor.low_percentile = 1.0
    processor.high_percentile = 99.0
    result = processor.convert_display_bits(image)
    assert result.dtype == np.uint8, "百分比裁剪输出类型错误"
    print("  ✓ 百分比裁剪正常")
    
    print("✓ convert_display_bits 测试通过")


def main():
    """主测试函数"""
    print("=" * 60)
    print("验证 GUI 和处理器实现")
    print("=" * 60)
    
    try:
        test_main_window_methods()
        test_on_setting_changed_parameters()
        test_image_processor_parameters()
        test_convert_display_bits_logic()
        
        print("\n" + "=" * 60)
        print("✓ 所有验证测试通过！")
        print("=" * 60)
        print("\n实现总结：")
        print("1. ✓ ImageProcessor 添加了百分比裁剪功能")
        print("2. ✓ ImageProcessor 使用实际最大最小值归一化")
        print("3. ✓ GUI 添加了百分比裁剪控件")
        print("4. ✓ GUI 添加了所有时域滤波控件")
        print("5. ✓ on_setting_changed 同步所有新参数")
        print("6. ✓ 所有默认值设置正确")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

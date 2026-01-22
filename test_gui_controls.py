#!/usr/bin/env python3
"""
测试 GUI 控件初始化和参数同步
验证所有新增的控件都能正确工作
"""
import sys
sys.path.insert(0, '.')

from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow


def test_gui_controls_exist():
    """测试所有控件是否正确创建"""
    print("\n测试 GUI 控件存在性...")
    
    app = QApplication(sys.argv)
    window = MainWindow()
    
    # 检查显示设置控件
    assert hasattr(window, 'percentile_clipping_cb'), "缺少百分比裁剪复选框"
    assert hasattr(window, 'low_percentile_spin'), "缺少低百分比旋转框"
    assert hasattr(window, 'high_percentile_spin'), "缺少高百分比旋转框"
    print("  ✓ 显示设置控件存在")
    
    # 检查时域滤波控件 - 基础
    assert hasattr(window, 'temporal_cb'), "缺少多帧平均复选框"
    assert hasattr(window, 'temporal_spin'), "缺少多帧平均窗口旋转框"
    print("  ✓ 多帧平均控件存在")
    
    # 检查时域滤波控件 - 时域中值
    assert hasattr(window, 'temporal_median_cb'), "缺少时域中值复选框"
    assert hasattr(window, 'temporal_median_spin'), "缺少时域中值窗口旋转框"
    print("  ✓ 时域中值滤波控件存在")
    
    # 检查时域滤波控件 - 非相干积累
    assert hasattr(window, 'incoherent_integration_cb'), "缺少非相干积累复选框"
    assert hasattr(window, 'incoherent_integration_spin'), "缺少非相干积累窗口旋转框"
    print("  ✓ 非相干积累控件存在")
    
    # 检查时域滤波控件 - 异常点剔除
    assert hasattr(window, 'outlier_rejection_cb'), "缺少异常点剔除复选框"
    assert hasattr(window, 'outlier_rejection_spin'), "缺少异常点剔除窗口旋转框"
    assert hasattr(window, 'outlier_sigma_spin'), "缺少异常点剔除 sigma 旋转框"
    print("  ✓ 异常点剔除累加控件存在")
    
    # 检查时域滤波控件 - 微弱目标处理
    assert hasattr(window, 'weak_target_cb'), "缺少微弱目标处理复选框"
    assert hasattr(window, 'weak_target_spin'), "缺少微弱目标处理窗口旋转框"
    print("  ✓ 微弱目标处理控件存在")
    
    print("✓ 所有 GUI 控件存在性测试通过")
    
    return window


def test_initial_values():
    """测试控件初始值"""
    print("\n测试控件初始值...")
    
    app = QApplication(sys.argv)
    window = MainWindow()
    
    # 检查百分比裁剪初始值
    assert window.low_percentile_spin.value() == 1, "低百分比初始值应为 1"
    assert window.high_percentile_spin.value() == 99, "高百分比初始值应为 99"
    print("  ✓ 百分比裁剪初始值正确")
    
    # 检查时域滤波初始值
    assert window.temporal_median_spin.value() == 5, "时域中值窗口初始值应为 5"
    assert window.incoherent_integration_spin.value() == 5, "非相干积累窗口初始值应为 5"
    assert window.outlier_rejection_spin.value() == 5, "异常点剔除窗口初始值应为 5"
    assert window.outlier_sigma_spin.value() == 2, "Sigma 初始值应为 2"
    assert window.weak_target_spin.value() == 7, "微弱目标窗口初始值应为 7"
    print("  ✓ 时域滤波初始值正确")
    
    print("✓ 控件初始值测试通过")


def test_parameter_sync():
    """测试参数同步到 processor"""
    print("\n测试参数同步...")
    
    app = QApplication(sys.argv)
    window = MainWindow()
    
    # 测试百分比裁剪参数同步
    window.percentile_clipping_cb.setChecked(True)
    window.low_percentile_spin.setValue(2)
    window.high_percentile_spin.setValue(98)
    window.on_setting_changed()
    
    assert window.processor.enable_percentile_clipping == True, "百分比裁剪开关同步失败"
    assert window.processor.low_percentile == 2.0, "低百分比同步失败"
    assert window.processor.high_percentile == 98.0, "高百分比同步失败"
    print("  ✓ 百分比裁剪参数同步成功")
    
    # 测试时域中值滤波参数同步
    window.temporal_median_cb.setChecked(True)
    window.temporal_median_spin.setValue(7)
    window.on_setting_changed()
    
    assert window.processor.enable_temporal_median == True, "时域中值开关同步失败"
    assert window.processor.temporal_median_window == 7, "时域中值窗口同步失败"
    print("  ✓ 时域中值滤波参数同步成功")
    
    # 测试非相干积累参数同步
    window.incoherent_integration_cb.setChecked(True)
    window.incoherent_integration_spin.setValue(9)
    window.on_setting_changed()
    
    assert window.processor.enable_incoherent_integration == True, "非相干积累开关同步失败"
    assert window.processor.incoherent_integration_window == 9, "非相干积累窗口同步失败"
    print("  ✓ 非相干积累参数同步成功")
    
    # 测试异常点剔除参数同步
    window.outlier_rejection_cb.setChecked(True)
    window.outlier_rejection_spin.setValue(7)
    window.outlier_sigma_spin.setValue(3)
    window.on_setting_changed()
    
    assert window.processor.enable_outlier_rejection == True, "异常点剔除开关同步失败"
    assert window.processor.outlier_rejection_window == 7, "异常点剔除窗口同步失败"
    assert window.processor.outlier_sigma == 3.0, "Sigma 参数同步失败"
    print("  ✓ 异常点剔除参数同步成功")
    
    # 测试微弱目标处理参数同步
    window.weak_target_cb.setChecked(True)
    window.weak_target_spin.setValue(9)
    window.on_setting_changed()
    
    assert window.processor.enable_weak_target_processing == True, "微弱目标处理开关同步失败"
    assert window.processor.weak_target_window == 9, "微弱目标处理窗口同步失败"
    print("  ✓ 微弱目标处理参数同步成功")
    
    print("✓ 参数同步测试通过")


def test_processor_parameters():
    """测试处理器参数是否正确初始化"""
    print("\n测试处理器参数初始化...")
    
    app = QApplication(sys.argv)
    window = MainWindow()
    processor = window.processor
    
    # 检查百分比裁剪参数
    assert hasattr(processor, 'enable_percentile_clipping'), "处理器缺少 enable_percentile_clipping"
    assert hasattr(processor, 'low_percentile'), "处理器缺少 low_percentile"
    assert hasattr(processor, 'high_percentile'), "处理器缺少 high_percentile"
    assert processor.low_percentile == 1.0, "低百分比默认值应为 1.0"
    assert processor.high_percentile == 99.0, "高百分比默认值应为 99.0"
    print("  ✓ 百分比裁剪参数正确")
    
    # 检查时域滤波参数
    assert hasattr(processor, 'enable_temporal_median'), "处理器缺少 enable_temporal_median"
    assert hasattr(processor, 'temporal_median_window'), "处理器缺少 temporal_median_window"
    assert hasattr(processor, 'enable_incoherent_integration'), "处理器缺少 enable_incoherent_integration"
    assert hasattr(processor, 'incoherent_integration_window'), "处理器缺少 incoherent_integration_window"
    assert hasattr(processor, 'enable_outlier_rejection'), "处理器缺少 enable_outlier_rejection"
    assert hasattr(processor, 'outlier_rejection_window'), "处理器缺少 outlier_rejection_window"
    assert hasattr(processor, 'outlier_sigma'), "处理器缺少 outlier_sigma"
    assert hasattr(processor, 'enable_weak_target_processing'), "处理器缺少 enable_weak_target_processing"
    assert hasattr(processor, 'weak_target_window'), "处理器缺少 weak_target_window"
    print("  ✓ 时域滤波参数正确")
    
    print("✓ 处理器参数初始化测试通过")


def main():
    """主测试函数"""
    print("=" * 60)
    print("测试 GUI 控件和参数同步")
    print("=" * 60)
    
    try:
        test_gui_controls_exist()
        test_initial_values()
        test_parameter_sync()
        test_processor_parameters()
        
        print("\n" + "=" * 60)
        print("✓ 所有 GUI 测试通过！")
        print("=" * 60)
        print("\n新增功能总结：")
        print("1. ✓ 百分比裁剪控件（复选框 + 两个百分比旋转框）")
        print("2. ✓ 时域中值滤波控件（复选框 + 窗口大小）")
        print("3. ✓ 非相干积累控件（复选框 + 窗口大小）")
        print("4. ✓ 异常点剔除累加控件（复选框 + 窗口大小 + sigma）")
        print("5. ✓ 微弱目标处理控件（复选框 + 窗口大小）")
        print("6. ✓ 所有参数正确同步到 processor")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

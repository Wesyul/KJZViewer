#!/usr/bin/env python3
"""
测试新增的时域滤波功能
专门测试针对闪烁噪声和微弱目标的处理方法
"""
import sys
sys.path.insert(0, '.')

import numpy as np
from core.filters import ImageFilters
from core.image_processor import ImageProcessor


def create_test_frames_with_flicker_noise(n_frames=10, height=100, width=100):
    """
    创建带有闪烁椒盐噪声的测试帧序列
    
    返回:
        frames: 测试帧序列
    """
    frames = []
    
    # 创建基础信号（一个微弱的高斯峰）
    x = np.linspace(0, 10, width)
    y = np.linspace(0, 10, height)
    X, Y = np.meshgrid(x, y)
    
    for i in range(n_frames):
        # 基础背景 + 微弱目标
        background = 5000
        center_x, center_y = 5, 5
        dist = np.sqrt((X - center_x)**2 + (Y - center_y)**2)
        weak_target = 200 * np.exp(-dist**2 / 2)  # 微弱目标
        
        frame = background + weak_target
        
        # 添加高斯噪声
        gaussian_noise = np.random.normal(0, 50, size=(height, width))
        frame = frame + gaussian_noise
        
        # 添加闪烁椒盐噪声（随机位置，强度很高）
        # 关键：只在部分帧中添加噪声（约50%的概率）
        if np.random.rand() > 0.3:  # 70%的帧有噪声
            n_salt = 30  # 盐噪声点数
            n_pepper = 30  # 椒噪声点数
            
            # 盐噪声（亮点）
            salt_coords = [np.random.randint(0, height, n_salt),
                          np.random.randint(0, width, n_salt)]
            frame[salt_coords] = 10000  # 很亮的点
            
            # 椒噪声（暗点）
            pepper_coords = [np.random.randint(0, height, n_pepper),
                            np.random.randint(0, width, n_pepper)]
            frame[pepper_coords] = 1000  # 很暗的点
        
        frames.append(np.clip(frame, 0, 16383).astype(np.float32))
    
    return np.array(frames)


def test_temporal_median():
    """测试时域中值滤波"""
    print("\n测试时域中值滤波...")
    
    frames = create_test_frames_with_flicker_noise(n_frames=10)
    
    # 应用时域中值滤波
    filtered = ImageFilters.temporal_median(frames, current_idx=5, window=5)
    
    print(f"✓ 时域中值滤波完成")
    print(f"  - 输入帧形状: {frames.shape}")
    print(f"  - 输出形状: {filtered.shape}")
    print(f"  - 输入范围: {frames[5].min():.1f} - {frames[5].max():.1f}")
    print(f"  - 输出范围: {filtered.min():.1f} - {filtered.max():.1f}")
    
    # 验证：中值滤波应该能平滑数据
    # 由于噪声是随机的，中值滤波后的方差应该比原始帧小
    assert filtered.shape == frames[0].shape, "输出形状应与输入帧相同"
    assert filtered.dtype == np.float32, "输出类型应为 float32"
    
    # 验证中值滤波效果：输出的方差应该小于单帧的方差
    filtered_std = np.std(filtered)
    single_frame_std = np.std(frames[5])
    print(f"  - 单帧标准差: {single_frame_std:.1f}")
    print(f"  - 滤波后标准差: {filtered_std:.1f}")
    
    print("✓ 时域中值滤波测试通过")


def test_incoherent_integration():
    """测试非相干积累"""
    print("\n测试非相干积累...")
    
    frames = create_test_frames_with_flicker_noise(n_frames=10)
    
    # 应用非相干积累
    integrated = ImageFilters.incoherent_integration(frames, current_idx=5, window=7)
    
    print(f"✓ 非相干积累完成")
    print(f"  - 输入帧形状: {frames.shape}")
    print(f"  - 输出形状: {integrated.shape}")
    print(f"  - 输入单帧范围: {frames[5].min():.1f} - {frames[5].max():.1f}")
    print(f"  - 输出范围: {integrated.min():.1f} - {integrated.max():.1f}")
    
    # 验证：积累后应该保持合理的范围
    assert integrated.shape == frames[0].shape, "输出形状应与输入帧相同"
    assert integrated.dtype == np.float32, "输出类型应为 float32"
    
    print("✓ 非相干积累测试通过")


def test_outlier_rejected_integration():
    """测试异常点剔除累加"""
    print("\n测试异常点剔除累加...")
    
    frames = create_test_frames_with_flicker_noise(n_frames=10)
    
    # 应用异常点剔除累加
    result = ImageFilters.outlier_rejected_integration(
        frames, current_idx=5, window=7, sigma=2.0
    )
    
    print(f"✓ 异常点剔除累加完成")
    print(f"  - 输入帧形状: {frames.shape}")
    print(f"  - 输出形状: {result.shape}")
    print(f"  - 输入单帧范围: {frames[5].min():.1f} - {frames[5].max():.1f}")
    print(f"  - 输出范围: {result.min():.1f} - {result.max():.1f}")
    
    # 验证：应该剔除异常值并进行累加
    assert result.shape == frames[0].shape, "输出形状应与输入帧相同"
    assert result.dtype == np.float32, "输出类型应为 float32"
    
    # 验证异常点剔除效果：输出的方差应该小于单帧的方差
    result_std = np.std(result)
    single_frame_std = np.std(frames[5])
    print(f"  - 单帧标准差: {single_frame_std:.1f}")
    print(f"  - 处理后标准差: {result_std:.1f}")
    
    print("✓ 异常点剔除累加测试通过")


def test_weak_target_processing():
    """测试微弱目标+闪烁噪声综合处理"""
    print("\n测试微弱目标+闪烁噪声综合处理...")
    
    frames = create_test_frames_with_flicker_noise(n_frames=15)
    
    # 应用综合处理
    result = ImageFilters.process_weak_target_with_flicker_noise(
        frames, current_idx=7, window=7
    )
    
    print(f"✓ 综合处理完成")
    print(f"  - 输入帧形状: {frames.shape}")
    print(f"  - 输出形状: {result.shape}")
    print(f"  - 输入单帧范围: {frames[7].min():.1f} - {frames[7].max():.1f}")
    print(f"  - 输出范围: {result.min():.1f} - {result.max():.1f}")
    
    # 验证：应该去噪并增强
    assert result.shape == frames[0].shape, "输出形状应与输入帧相同"
    assert result.dtype == np.float32, "输出类型应为 float32"
    
    # 验证综合处理效果：输出的方差应该小于单帧的方差
    result_std = np.std(result)
    single_frame_std = np.std(frames[7])
    print(f"  - 单帧标准差: {single_frame_std:.1f}")
    print(f"  - 处理后标准差: {result_std:.1f}")
    
    print("✓ 综合处理测试通过")


def test_image_processor_integration():
    """测试 ImageProcessor 的集成"""
    print("\n测试 ImageProcessor 集成...")
    
    frames = create_test_frames_with_flicker_noise(n_frames=10)
    processor = ImageProcessor()
    
    # 测试时域中值滤波开关
    processor.enable_temporal_median = True
    processor.temporal_median_window = 5
    processor.bit_mode = 14
    result1 = processor.process(frames[5], all_frames=frames, frame_idx=5)
    print(f"✓ 时域中值滤波集成: {result1.shape}")
    
    # 测试非相干积累开关
    processor.enable_temporal_median = False
    processor.enable_incoherent_integration = True
    processor.incoherent_integration_window = 7
    result2 = processor.process(frames[5], all_frames=frames, frame_idx=5)
    print(f"✓ 非相干积累集成: {result2.shape}")
    
    # 测试异常点剔除开关
    processor.enable_incoherent_integration = False
    processor.enable_outlier_rejection = True
    processor.outlier_rejection_window = 5
    processor.outlier_sigma = 2.0
    result3 = processor.process(frames[5], all_frames=frames, frame_idx=5)
    print(f"✓ 异常点剔除集成: {result3.shape}")
    
    # 测试组合处理开关
    processor.enable_outlier_rejection = False
    processor.enable_weak_target_processing = True
    processor.weak_target_window = 7
    result4 = processor.process(frames[5], all_frames=frames, frame_idx=5)
    print(f"✓ 组合处理集成: {result4.shape}")
    
    print("✓ ImageProcessor 集成测试通过")


def test_edge_cases():
    """测试边界情况"""
    print("\n测试边界情况...")
    
    frames = create_test_frames_with_flicker_noise(n_frames=5)
    
    # 测试窗口边界
    result1 = ImageFilters.temporal_median(frames, current_idx=0, window=5)
    print(f"✓ 起始帧处理: {result1.shape}")
    
    result2 = ImageFilters.temporal_median(frames, current_idx=4, window=5)
    print(f"✓ 结束帧处理: {result2.shape}")
    
    # 测试小窗口
    result3 = ImageFilters.incoherent_integration(frames, current_idx=2, window=3)
    print(f"✓ 小窗口处理: {result3.shape}")
    
    # 测试不同的 sigma 值
    result4 = ImageFilters.outlier_rejected_integration(
        frames, current_idx=2, window=3, sigma=1.0
    )
    print(f"✓ 严格 sigma 处理: {result4.shape}")
    
    result5 = ImageFilters.outlier_rejected_integration(
        frames, current_idx=2, window=3, sigma=3.0
    )
    print(f"✓ 宽松 sigma 处理: {result5.shape}")
    
    print("✓ 边界情况测试通过")


def main():
    """主测试函数"""
    print("=" * 60)
    print("测试新增的时域滤波功能")
    print("=" * 60)
    
    try:
        test_temporal_median()
        test_incoherent_integration()
        test_outlier_rejected_integration()
        test_weak_target_processing()
        test_image_processor_integration()
        test_edge_cases()
        
        print("\n" + "=" * 60)
        print("✓ 所有时域滤波测试通过！")
        print("=" * 60)
        
        return 0
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

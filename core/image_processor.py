"""
图像处理管线
集成各种处理功能
"""
import numpy as np
import cv2
from .filters import ImageFilters


class ImageProcessor:
    """图像处理器"""
    
    def __init__(self):
        """初始化处理器"""
        self.background = None
        self.filters = ImageFilters()
        
        # 处理参数
        self.enable_background_subtraction = False
        self.enable_gaussian = False
        self.enable_median = False
        self.enable_bilateral = False
        self.enable_temporal = False
        self.enable_auto_contrast = False
        
        # 新增：时域高级滤波开关
        self.enable_temporal_median = False
        self.enable_incoherent_integration = False
        self.enable_outlier_rejection = False
        self.enable_weak_target_processing = False
        
        # 滤波参数
        self.gaussian_kernel = 5
        self.median_kernel = 3
        self.bilateral_d = 9
        self.bilateral_sigma_color = 75
        self.bilateral_sigma_space = 75
        self.temporal_window = 5
        
        # 新增：时域高级滤波参数
        self.temporal_median_window = 5
        self.incoherent_integration_window = 5
        self.outlier_rejection_window = 5
        self.outlier_sigma = 2.0
        self.weak_target_window = 7
        
        # 显示参数
        self.bit_mode = 8  # 8 或 14
        
        # 百分比裁剪参数
        self.enable_percentile_clipping = False
        self.low_percentile = 1.0  # 下限百分比（排除最暗的1%）
        self.high_percentile = 99.0  # 上限百分比（排除最亮的1%）
        
    def set_background(self, background: np.ndarray):
        """
        设置背景图像
        
        参数:
            background: 背景图像数组
        """
        self.background = background.copy() if background is not None else None
    
    def convert_display_bits(self, image: np.ndarray) -> np.ndarray:
        """
        转换显示位数
        
        参数:
            image: 输入图像
            
        返回:
            转换后的图像
        """
        if self.bit_mode == 8:
            # 16bit -> 8bit 线性映射
            # 默认使用实际最大最小值归一化（而不是理论最大值）
            if self.enable_percentile_clipping:
                # 使用百分比裁剪：排除极端噪点
                min_val = np.percentile(image, self.low_percentile)
                max_val = np.percentile(image, self.high_percentile)
            else:
                # 使用实际最大最小值
                min_val, max_val = image.min(), image.max()
            
            if max_val > min_val:
                normalized = (image - min_val) / (max_val - min_val)
                # 裁剪到 [0, 1] 范围（当使用百分比裁剪时，超出百分位范围的像素值可能超出 [0,1]）
                normalized = np.clip(normalized, 0, 1)
            else:
                normalized = np.zeros_like(image, dtype=np.float32)
                
            return (normalized * 255).astype(np.uint8)
        else:
            # 保持 14-bit 原始位数
            # 也使用实际动态范围进行归一化
            if self.enable_percentile_clipping:
                min_val = np.percentile(image, self.low_percentile)
                max_val = np.percentile(image, self.high_percentile)
            else:
                min_val, max_val = image.min(), image.max()
            
            if max_val > min_val:
                normalized = (image - min_val) / (max_val - min_val)
                # 裁剪到 [0, 1] 范围（当使用百分比裁剪时，超出百分位范围的像素值可能超出 [0,1]）
                normalized = np.clip(normalized, 0, 1)
                return (normalized * 16383).astype(np.uint16)
            else:
                return image.astype(np.uint16)
    
    def apply_auto_contrast(self, image: np.ndarray) -> np.ndarray:
        """
        自动对比度增强（动态范围拉伸）
        
        参数:
            image: 输入图像
            
        返回:
            增强后的图像
        """
        img_min, img_max = image.min(), image.max()
        
        if img_max > img_min:
            # 拉伸到全范围
            if self.bit_mode == 14:
                max_val = 16383  # 2^14 - 1
            else:
                max_val = 255
            
            normalized = (image - img_min) / (img_max - img_min)
            return normalized * max_val
        
        return image
    
    def process(self, image, all_frames=None, frame_idx=0) -> np.ndarray:
        """
        完整的图像处理管线
        
        参数:
            image: 输入图像
            all_frames: 所有帧数据（用于时域滤波）
            frame_idx: 当前帧索引
            
        返回:
            处理后的图像
        """
        result = image.astype(np.float32)
        
        # 1. 背景减除
        if self.enable_background_subtraction and self.background is not None:
            result = self.filters.subtract_background(result, self.background)
        
        # 2. 时域滤波（需要多帧数据）
        # 注意：建议处理顺序是先去噪再增强
        if all_frames is not None:
            # 2.1 组合处理：微弱目标+闪烁噪声的一键处理
            if self.enable_weak_target_processing:
                result = self.filters.process_weak_target_with_flicker_noise(
                    all_frames, frame_idx, self.weak_target_window
                )
            else:
                # 2.2 去噪处理（优先级：异常点剔除 > 时域中值 > 普通时域平均）
                if self.enable_outlier_rejection:
                    result = self.filters.outlier_rejected_integration(
                        all_frames, frame_idx, 
                        self.outlier_rejection_window, 
                        self.outlier_sigma
                    )
                elif self.enable_temporal_median:
                    result = self.filters.temporal_median(
                        all_frames, frame_idx, self.temporal_median_window
                    )
                elif self.enable_temporal:
                    result = self.filters.temporal_average(
                        all_frames, frame_idx, self.temporal_window
                    )
                
                # 2.3 增强处理：非相干积累（在去噪之后应用）
                if self.enable_incoherent_integration and not self.enable_outlier_rejection:
                    # 注意：如果已经使用异常点剔除累加，就不需要再做非相干积累
                    result = self.filters.incoherent_integration(
                        all_frames, frame_idx, self.incoherent_integration_window
                    )
        
        # 3. 空域滤波
        if self.enable_gaussian:
            result = self.filters.gaussian_blur(result, self.gaussian_kernel)
        
        if self.enable_median:
            result = self.filters.median_filter(result, self.median_kernel)
        
        if self.enable_bilateral:
            result = self.filters.bilateral_filter(
                result, 
                self.bilateral_d,
                self.bilateral_sigma_color,
                self.bilateral_sigma_space
            )
        
        # 4. 自动对比度
        if self.enable_auto_contrast:
            result = self.apply_auto_contrast(result)
        
        # 5. 位深度转换
        result = self.convert_display_bits(result)
        
        return result

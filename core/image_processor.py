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
        
        # 滤波参数
        self.gaussian_kernel = 5
        self.median_kernel = 3
        self.bilateral_d = 9
        self.bilateral_sigma_color = 75
        self.bilateral_sigma_space = 75
        self.temporal_window = 5
        
        # 显示参数
        self.bit_mode = 8  # 8 或 14
        
    def set_background(self, background: np.ndarray):
        """
        设置背景图像
        
        参数:
            background: 背景图像数组
        """
        self.background = background.copy() if background is not None else None
    
    def convert_display_bits(self, image: np.ndarray) -> np.ndarray:
        """
        位深度转换（14-bit -> 8-bit）
        
        参数:
            image: 输入图像
            
        返回:
            转换后的图像
        """
        if self.bit_mode == 8:
            # 线性映射到 8-bit
            img_min, img_max = image.min(), image.max()
            if img_max > img_min:
                normalized = (image - img_min) / (img_max - img_min)
                return (normalized * 255).astype(np.uint8)
            else:
                return np.zeros_like(image, dtype=np.uint8)
        else:
            # 保持 14-bit（实际使用 uint16）
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
        if self.enable_temporal and all_frames is not None:
            result = self.filters.temporal_average(all_frames, frame_idx, self.temporal_window)
        
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

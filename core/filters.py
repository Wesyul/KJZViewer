"""
图像滤波器集合
包含空域和时域滤波功能
"""
import cv2
import numpy as np
from scipy.ndimage import median_filter as scipy_median


class ImageFilters:
    """图像滤波器类"""
    
    @staticmethod
    def gaussian_blur(image, kernel_size=5):
        """
        高斯滤波
        
        参数:
            image: 输入图像
            kernel_size: 核大小（必须为奇数）
            
        返回:
            滤波后的图像
        """
        if kernel_size % 2 == 0:
            kernel_size += 1  # 确保为奇数
        
        return cv2.GaussianBlur(image.astype(np.float32), (kernel_size, kernel_size), 0)
    
    @staticmethod
    def median_filter(image, kernel_size=3):
        """
        中值滤波
        
        参数:
            image: 输入图像
            kernel_size: 核大小
            
        返回:
            滤波后的图像
        """
        if kernel_size % 2 == 0:
            kernel_size += 1  # 确保为奇数
        
        return cv2.medianBlur(image.astype(np.uint16), kernel_size).astype(np.float32)
    
    @staticmethod
    def bilateral_filter(image, d=9, sigma_color=75, sigma_space=75):
        """
        双边滤波（保边平滑）
        
        参数:
            image: 输入图像
            d: 滤波器直径
            sigma_color: 颜色空间标准差
            sigma_space: 坐标空间标准差
            
        返回:
            滤波后的图像
        """
        # 归一化到 0-255 范围用于双边滤波
        img_normalized = cv2.normalize(image.astype(np.float32), None, 0, 255, cv2.NORM_MINMAX)
        img_8bit = img_normalized.astype(np.uint8)
        
        # 应用双边滤波
        filtered = cv2.bilateralFilter(img_8bit, d, sigma_color, sigma_space)
        
        # 映射回原始范围
        img_min, img_max = image.min(), image.max()
        result = filtered.astype(np.float32) / 255.0 * (img_max - img_min) + img_min
        
        return result
    
    @staticmethod
    def temporal_average(frames, current_idx, window=5):
        """
        时域滑动平均滤波
        
        参数:
            frames: 所有帧数据 (n_frames, height, width)
            current_idx: 当前帧索引
            window: 滑动窗口大小
            
        返回:
            平均后的图像
        """
        if frames is None or len(frames) == 0:
            raise ValueError("帧数据为空")
        
        n_frames = len(frames)
        half_window = window // 2
        
        # 计算窗口范围
        start_idx = max(0, current_idx - half_window)
        end_idx = min(n_frames, current_idx + half_window + 1)
        
        # 计算平均
        selected_frames = frames[start_idx:end_idx]
        return np.mean(selected_frames, axis=0).astype(np.float32)
    
    @staticmethod
    def subtract_background(image, background):
        """
        背景减除
        
        参数:
            image: 输入图像
            background: 背景图像
            
        返回:
            减背景后的图像
        """
        if background is None:
            return image
        
        # 减背景并处理负值
        result = image.astype(np.float32) - background.astype(np.float32)
        result = np.maximum(result, 0)  # 负值截断为 0
        
        return result

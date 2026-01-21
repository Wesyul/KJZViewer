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
    
    @staticmethod
    def temporal_median(frames, current_idx, window=5):
        """
        时域中值滤波 - 对闪烁椒盐噪声特别有效
        
        通过对同一像素位置取多帧的中值，可以有效剔除时间上随机出现的闪烁噪声。
        由于椒盐噪声在时间轴上是异常值，中值滤波能够稳健地去除这些噪声点。
        
        参数:
            frames: 所有帧数据 (n_frames, height, width)
            current_idx: 当前帧索引
            window: 滑动窗口大小
            
        返回:
            中值滤波后的图像
        """
        if frames is None or len(frames) == 0:
            raise ValueError("帧数据为空")
        
        n_frames = len(frames)
        half_window = window // 2
        
        # 计算窗口范围
        start_idx = max(0, current_idx - half_window)
        end_idx = min(n_frames, current_idx + half_window + 1)
        
        # 选取窗口内的帧
        selected_frames = frames[start_idx:end_idx]
        
        # 沿时间轴计算中值
        result = np.median(selected_frames, axis=0).astype(np.float32)
        
        return result
    
    @staticmethod
    def incoherent_integration(frames, current_idx, window=5):
        """
        非相干积累 - 提升微弱目标信噪比
        
        对多帧幅度进行累加，可以提升信噪比约 sqrt(N) 倍，其中 N 为累加帧数。
        适用于增强微弱目标，使其在背景噪声中更易被检测。
        
        参数:
            frames: 所有帧数据 (n_frames, height, width)
            current_idx: 当前帧索引  
            window: 累加窗口大小
            
        返回:
            累加后的图像（归一化到原始范围）
        """
        if frames is None or len(frames) == 0:
            raise ValueError("帧数据为空")
        
        n_frames = len(frames)
        half_window = window // 2
        
        # 计算窗口范围
        start_idx = max(0, current_idx - half_window)
        end_idx = min(n_frames, current_idx + half_window + 1)
        
        # 选取窗口内的帧并累加
        selected_frames = frames[start_idx:end_idx]
        accumulated = np.sum(selected_frames.astype(np.float64), axis=0)
        
        # 归一化：除以实际累加的帧数，保持原始幅度范围
        actual_window = end_idx - start_idx
        result = (accumulated / actual_window).astype(np.float32)
        
        return result
    
    @staticmethod
    def outlier_rejected_integration(frames, current_idx, window=5, sigma=2.0):
        """
        异常点剔除累加 - 剔除闪烁噪声后累加
        
        对每个像素的时间序列进行异常值检测（基于标准差），剔除异常值后再累加。
        这种方法结合了去噪和信噪比增强的效果，特别适合同时处理闪烁噪声和微弱目标。
        
        参数:
            frames: 所有帧数据 (n_frames, height, width)
            current_idx: 当前帧索引
            window: 滑动窗口大小
            sigma: 异常值剔除阈值（几倍标准差）
            
        返回:
            处理后的图像
        """
        if frames is None or len(frames) == 0:
            raise ValueError("帧数据为空")
        
        n_frames = len(frames)
        half_window = window // 2
        
        # 计算窗口范围
        start_idx = max(0, current_idx - half_window)
        end_idx = min(n_frames, current_idx + half_window + 1)
        
        # 选取窗口内的帧
        selected_frames = frames[start_idx:end_idx].astype(np.float64)
        
        # 计算每个像素时间序列的均值和标准差
        mean_val = np.mean(selected_frames, axis=0)
        std_val = np.std(selected_frames, axis=0)
        
        # 创建掩码：标记异常值
        # 对每一帧，判断哪些像素是异常值
        lower_bound = mean_val - sigma * std_val
        upper_bound = mean_val + sigma * std_val
        
        # 初始化结果和计数
        result = np.zeros_like(mean_val, dtype=np.float64)
        count = np.zeros_like(mean_val, dtype=np.float64)
        
        # 对每一帧进行处理
        for i in range(selected_frames.shape[0]):
            frame = selected_frames[i]
            # 创建有效像素掩码（非异常值）
            valid_mask = (frame >= lower_bound) & (frame <= upper_bound)
            result += frame * valid_mask
            count += valid_mask
        
        # 避免除零：如果某个像素所有值都被剔除，使用均值
        count = np.maximum(count, 1)
        result = result / count
        
        return result.astype(np.float32)
    
    @staticmethod
    def process_weak_target_with_flicker_noise(frames, current_idx, window=7):
        """
        微弱目标+闪烁噪声的综合处理
        
        这是一个组合处理方法，专门针对"闪烁椒盐噪声+微弱目标"的场景：
        1. 先用时域中值去除闪烁噪声
        2. 再进行多帧累加增强目标
        
        这种两步处理可以有效去除噪声同时增强微弱目标的可见度。
        
        参数:
            frames: 所有帧数据 (n_frames, height, width)
            current_idx: 当前帧索引
            window: 处理窗口大小
            
        返回:
            处理后的图像
        """
        if frames is None or len(frames) == 0:
            raise ValueError("帧数据为空")
        
        # 第一步：对每一帧进行时域中值滤波去噪
        # 创建一个临时数组存储去噪后的帧
        n_frames = len(frames)
        half_window = window // 2
        start_idx = max(0, current_idx - half_window)
        end_idx = min(n_frames, current_idx + half_window + 1)
        
        denoised_frames = []
        for i in range(start_idx, end_idx):
            denoised = ImageFilters.temporal_median(frames, i, window=min(5, window))
            denoised_frames.append(denoised)
        
        denoised_frames = np.array(denoised_frames)
        
        # 第二步：对去噪后的帧进行非相干积累
        accumulated = np.mean(denoised_frames, axis=0).astype(np.float32)
        
        return accumulated

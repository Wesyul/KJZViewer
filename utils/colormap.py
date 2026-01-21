"""
伪彩色映射工具
"""
import cv2
import numpy as np


class ColormapConverter:
    """伪彩色映射转换器"""
    
    # 支持的色彩映射
    COLORMAPS = {
        '灰度': None,  # 不应用映射
        'Jet': cv2.COLORMAP_JET,
        'Hot': cv2.COLORMAP_HOT,
        'Inferno': cv2.COLORMAP_INFERNO,
        'Viridis': cv2.COLORMAP_VIRIDIS,
        'Turbo': cv2.COLORMAP_TURBO,
        'Rainbow': cv2.COLORMAP_RAINBOW,
        'Ocean': cv2.COLORMAP_OCEAN,
        'Parula': cv2.COLORMAP_PARULA,
    }
    
    @staticmethod
    def apply_colormap(image: np.ndarray, colormap_name: str = '灰度') -> np.ndarray:
        """
        应用伪彩色映射
        
        参数:
            image: 输入图像（8-bit）
            colormap_name: 色彩映射名称
            
        返回:
            RGB 彩色图像
        """
        if colormap_name not in ColormapConverter.COLORMAPS:
            colormap_name = '灰度'
        
        colormap = ColormapConverter.COLORMAPS[colormap_name]
        
        # 确保输入为 8-bit
        if image.dtype != np.uint8:
            img_min, img_max = image.min(), image.max()
            if img_max > img_min:
                image_normalized = (image - img_min) / (img_max - img_min)
                image = (image_normalized * 255).astype(np.uint8)
            else:
                image = np.zeros_like(image, dtype=np.uint8)
        
        if colormap is None or colormap_name == '灰度':
            # 灰度图转 RGB
            return cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        else:
            # 应用伪彩色映射
            return cv2.applyColorMap(image, colormap)
    
    @staticmethod
    def get_available_colormaps():
        """
        获取可用的色彩映射列表
        
        返回:
            色彩映射名称列表
        """
        return list(ColormapConverter.COLORMAPS.keys())

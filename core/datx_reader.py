"""
DatX 文件读取模块
读取 640×512 14-bit 红外图像数据（小端序）
"""
import numpy as np
from pathlib import Path


class DatxReader:
    """DatX 格式红外图像读取器"""
    
    def __init__(self, width=640, height=512, bit_depth=14, little_endian=True):
        """
        初始化读取器
        
        参数:
            width: 图像宽度（默认 640）
            height: 图像高度（默认 512）
            bit_depth: 位深度（默认 14-bit）
            little_endian: 是否小端序（默认 True）
        """
        self.width = width
        self.height = height
        self.bit_depth = bit_depth
        self.little_endian = little_endian
        self.data = None
        self.file_path = None
        
    def load(self, file_path: str) -> np.ndarray:
        """
        加载 DatX 文件
        
        参数:
            file_path: 文件路径
            
        返回:
            shape 为 (n_frames, height, width) 的 numpy 数组
        """
        self.file_path = file_path
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 读取原始二进制数据
        with open(file_path, 'rb') as f:
            raw_data = f.read()
        
        # 计算每帧的字节数（每个像素 2 字节，uint16）
        frame_size_bytes = self.width * self.height * 2
        total_bytes = len(raw_data)
        
        # 计算帧数
        n_frames = total_bytes // frame_size_bytes
        
        if total_bytes % frame_size_bytes != 0:
            print(f"警告: 文件大小不是完整帧的整数倍，截断 {total_bytes % frame_size_bytes} 字节")
        
        # 读取为 uint16 数组
        dtype = '<u2' if self.little_endian else '>u2'
        data = np.frombuffer(raw_data[:n_frames * frame_size_bytes], dtype=dtype)
        
        # 提取有效的 14-bit 数据
        if self.bit_depth == 14:
            data = data & 0x3FFF
        
        # 重塑为 (n_frames, height, width)
        self.data = data.reshape((n_frames, self.height, self.width))
        
        return self.data
    
    def get_frame(self, index: int) -> np.ndarray:
        """
        获取指定帧
        
        参数:
            index: 帧索引
            
        返回:
            shape 为 (height, width) 的单帧图像
        """
        if self.data is None:
            raise RuntimeError("尚未加载数据，请先调用 load() 方法")
        
        if index < 0 or index >= len(self.data):
            raise IndexError(f"帧索引超出范围: {index} (总帧数: {len(self.data)})")
        
        return self.data[index]
    
    def get_frame_count(self) -> int:
        """
        获取总帧数
        
        返回:
            总帧数
        """
        if self.data is None:
            return 0
        return len(self.data)

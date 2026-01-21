"""
DatX 文件读取模块
读取 640×512 红外图像数据（小端序，uint16）
"""
import numpy as np
from pathlib import Path


class DatxReader:
    """读取 .datx 红外图像文件（与 MATLAB 逻辑一致）"""
    
    def __init__(self, width=640, height=512, little_endian=True):
        """
        初始化读取器
        
        参数:
            width: 图像宽度 (W=640)
            height: 图像高度 (H=512)
            little_endian: 小端序 (对应 MATLAB 'ieee-le')
        """
        self.width = width
        self.height = height
        self.little_endian = little_endian
        self.frames = None
        self.n_frames = 0
        self.file_path = None
        
    def load(self, file_path: str) -> np.ndarray:
        """
        加载 datx 文件
        
        与 MATLAB 代码等价:
            raw_data = fread(fid, inf, 'uint16=>uint16');
            num_frames = floor(length(raw_data) / pixels_per_frame);
            img = reshape(frame_data, [W H])';
        """
        self.file_path = Path(file_path)
        dtype = np.dtype('<u2' if self.little_endian else '>u2')  # uint16
        
        # 读取全部数据
        raw_data = np.fromfile(self.file_path, dtype=dtype)
        
        pixels_per_frame = self.width * self.height
        
        # 向下取整，丢弃尾部残留数据（与 MATLAB floor 一致）
        self.n_frames = len(raw_data) // pixels_per_frame
        
        if self.n_frames == 0:
            raise ValueError(
                f"文件数据不足一帧: {len(raw_data)} 像素, "
                f"需要至少 {pixels_per_frame} 像素"
            )
        
        # 截取完整帧的数据
        valid_pixels = self.n_frames * pixels_per_frame
        data = raw_data[:valid_pixels]
        
        # reshape: 与 MATLAB reshape(frame_data, [W H])' 等价
        # MATLAB 是列优先，所以先 reshape 成 (W, H, n_frames) 用 order='F'，再转置
        self.frames = data.reshape(self.width, self.height, self.n_frames, order='F')
        self.frames = np.transpose(self.frames, (2, 1, 0))  # (n_frames, H, W)
        
        return self.frames
    
    def get_frame(self, index: int) -> np.ndarray:
        """获取指定帧"""
        if self.frames is None:
            raise RuntimeError("请先加载文件")
        index = np.clip(index, 0, self.n_frames - 1)
        return self.frames[index]
    
    def get_frame_count(self) -> int:
        """获取总帧数"""
        return self.n_frames
    
    def get_file_info(self) -> dict:
        """获取文件信息"""
        return {
            'file_path': str(self.file_path) if self.file_path else None,
            'width': self.width,
            'height': self.height,
            'n_frames': self.n_frames,
            'dtype': 'uint16',
            'byte_order': 'little-endian' if self.little_endian else 'big-endian'
        }

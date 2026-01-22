"""
主窗口界面
PyQt5 GUI 实现
"""
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QSlider, QSpinBox, QComboBox,
    QGroupBox, QCheckBox, QFileDialog, QStatusBar, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
import numpy as np
import cv2
from pathlib import Path

from core.datx_reader import DatxReader
from core.image_processor import ImageProcessor
from utils.colormap import ColormapConverter


class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KJZ 红外图像查看器")
        self.setGeometry(100, 100, 1400, 900)
        
        # 数据存储
        self.reader = DatxReader()
        self.processor = ImageProcessor()
        self.colormap_converter = ColormapConverter()
        
        self.current_frame_idx = 0
        self.raw_frames = None
        self.current_image = None
        
        # 初始化界面
        self.init_ui()
        
    def init_ui(self):
        """初始化用户界面"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # 左侧：图像显示区
        left_layout = QVBoxLayout()
        
        # 图像标签
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(800, 600)
        self.image_label.setStyleSheet("border: 1px solid gray; background-color: black;")
        left_layout.addWidget(self.image_label)
        
        # 帧控制
        frame_control_layout = QHBoxLayout()
        self.frame_slider = QSlider(Qt.Horizontal)
        self.frame_slider.setMinimum(0)
        self.frame_slider.setMaximum(0)
        self.frame_slider.valueChanged.connect(self.on_frame_changed)
        frame_control_layout.addWidget(QLabel("帧:"))
        frame_control_layout.addWidget(self.frame_slider)
        
        self.frame_label = QLabel("0 / 0")
        frame_control_layout.addWidget(self.frame_label)
        
        left_layout.addLayout(frame_control_layout)
        
        main_layout.addLayout(left_layout, stretch=3)
        
        # 右侧：控制面板
        right_layout = QVBoxLayout()
        
        # 文件操作组
        file_group = self.create_file_group()
        right_layout.addWidget(file_group)
        
        # 显示设置组
        display_group = self.create_display_group()
        right_layout.addWidget(display_group)
        
        # 空域滤波组
        spatial_group = self.create_spatial_filter_group()
        right_layout.addWidget(spatial_group)
        
        # 时域滤波组
        temporal_group = self.create_temporal_filter_group()
        right_layout.addWidget(temporal_group)
        
        # 背景处理组
        background_group = self.create_background_group()
        right_layout.addWidget(background_group)
        
        right_layout.addStretch()
        
        main_layout.addLayout(right_layout, stretch=1)
        
        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
        
    def create_file_group(self):
        """创建文件操作组"""
        group = QGroupBox("文件操作")
        layout = QVBoxLayout()
        
        open_btn = QPushButton("打开 DatX 文件")
        open_btn.clicked.connect(self.open_file)
        layout.addWidget(open_btn)
        
        save_btn = QPushButton("保存当前帧")
        save_btn.clicked.connect(self.save_frame)
        layout.addWidget(save_btn)
        
        group.setLayout(layout)
        return group
    
    def create_display_group(self):
        """创建显示设置组"""
        group = QGroupBox("显示设置")
        layout = QVBoxLayout()
        
        # 位数选择
        bit_layout = QHBoxLayout()
        bit_layout.addWidget(QLabel("位深度:"))
        self.bit_combo = QComboBox()
        self.bit_combo.addItems(["8-bit", "14-bit"])
        self.bit_combo.currentTextChanged.connect(self.on_bit_mode_changed)
        bit_layout.addWidget(self.bit_combo)
        layout.addLayout(bit_layout)
        
        # 自动对比度
        self.auto_contrast_cb = QCheckBox("自动对比度")
        self.auto_contrast_cb.stateChanged.connect(self.on_setting_changed)
        layout.addWidget(self.auto_contrast_cb)
        
        # 百分比裁剪
        self.percentile_clipping_cb = QCheckBox("百分比裁剪（排除异常值）")
        self.percentile_clipping_cb.stateChanged.connect(self.on_setting_changed)
        layout.addWidget(self.percentile_clipping_cb)
        
        # 低百分比设置
        low_percentile_layout = QHBoxLayout()
        low_percentile_layout.addWidget(QLabel("  下限百分比:"))
        self.low_percentile_spin = QSpinBox()
        self.low_percentile_spin.setRange(0, 10)
        self.low_percentile_spin.setValue(1)
        self.low_percentile_spin.setSuffix("%")
        self.low_percentile_spin.valueChanged.connect(self.on_setting_changed)
        low_percentile_layout.addWidget(self.low_percentile_spin)
        layout.addLayout(low_percentile_layout)
        
        # 高百分比设置
        high_percentile_layout = QHBoxLayout()
        high_percentile_layout.addWidget(QLabel("  上限百分比:"))
        self.high_percentile_spin = QSpinBox()
        self.high_percentile_spin.setRange(90, 100)
        self.high_percentile_spin.setValue(99)
        self.high_percentile_spin.setSuffix("%")
        self.high_percentile_spin.valueChanged.connect(self.on_setting_changed)
        high_percentile_layout.addWidget(self.high_percentile_spin)
        layout.addLayout(high_percentile_layout)
        
        # 伪彩色映射
        colormap_layout = QHBoxLayout()
        colormap_layout.addWidget(QLabel("伪彩色:"))
        self.colormap_combo = QComboBox()
        self.colormap_combo.addItems(self.colormap_converter.get_available_colormaps())
        self.colormap_combo.currentTextChanged.connect(self.on_setting_changed)
        colormap_layout.addWidget(self.colormap_combo)
        layout.addLayout(colormap_layout)
        
        group.setLayout(layout)
        return group
    
    def create_spatial_filter_group(self):
        """创建空域滤波组"""
        group = QGroupBox("空域滤波")
        layout = QVBoxLayout()
        
        # 高斯滤波
        self.gaussian_cb = QCheckBox("高斯滤波")
        self.gaussian_cb.stateChanged.connect(self.on_setting_changed)
        layout.addWidget(self.gaussian_cb)
        
        gaussian_size_layout = QHBoxLayout()
        gaussian_size_layout.addWidget(QLabel("  核大小:"))
        self.gaussian_spin = QSpinBox()
        self.gaussian_spin.setRange(3, 15)
        self.gaussian_spin.setSingleStep(2)
        self.gaussian_spin.setValue(5)
        self.gaussian_spin.valueChanged.connect(self.on_setting_changed)
        gaussian_size_layout.addWidget(self.gaussian_spin)
        layout.addLayout(gaussian_size_layout)
        
        # 中值滤波
        self.median_cb = QCheckBox("中值滤波")
        self.median_cb.stateChanged.connect(self.on_setting_changed)
        layout.addWidget(self.median_cb)
        
        median_size_layout = QHBoxLayout()
        median_size_layout.addWidget(QLabel("  核大小:"))
        self.median_spin = QSpinBox()
        self.median_spin.setRange(3, 15)
        self.median_spin.setSingleStep(2)
        self.median_spin.setValue(3)
        self.median_spin.valueChanged.connect(self.on_setting_changed)
        median_size_layout.addWidget(self.median_spin)
        layout.addLayout(median_size_layout)
        
        # 双边滤波
        self.bilateral_cb = QCheckBox("双边滤波")
        self.bilateral_cb.stateChanged.connect(self.on_setting_changed)
        layout.addWidget(self.bilateral_cb)
        
        group.setLayout(layout)
        return group
    
    def create_temporal_filter_group(self):
        """创建时域滤波组"""
        group = QGroupBox("时域滤波")
        layout = QVBoxLayout()
        
        # 时域平均
        self.temporal_cb = QCheckBox("多帧平均")
        self.temporal_cb.stateChanged.connect(self.on_setting_changed)
        layout.addWidget(self.temporal_cb)
        
        temporal_window_layout = QHBoxLayout()
        temporal_window_layout.addWidget(QLabel("  窗口大小:"))
        self.temporal_spin = QSpinBox()
        self.temporal_spin.setRange(3, 21)
        self.temporal_spin.setSingleStep(2)
        self.temporal_spin.setValue(5)
        self.temporal_spin.valueChanged.connect(self.on_setting_changed)
        temporal_window_layout.addWidget(self.temporal_spin)
        layout.addLayout(temporal_window_layout)
        
        # 时域中值滤波
        self.temporal_median_cb = QCheckBox("时域中值滤波")
        self.temporal_median_cb.stateChanged.connect(self.on_setting_changed)
        layout.addWidget(self.temporal_median_cb)
        
        temporal_median_window_layout = QHBoxLayout()
        temporal_median_window_layout.addWidget(QLabel("  窗口大小:"))
        self.temporal_median_spin = QSpinBox()
        self.temporal_median_spin.setRange(3, 21)
        self.temporal_median_spin.setSingleStep(2)
        self.temporal_median_spin.setValue(5)
        self.temporal_median_spin.valueChanged.connect(self.on_setting_changed)
        temporal_median_window_layout.addWidget(self.temporal_median_spin)
        layout.addLayout(temporal_median_window_layout)
        
        # 非相干积累
        self.incoherent_integration_cb = QCheckBox("非相干积累")
        self.incoherent_integration_cb.stateChanged.connect(self.on_setting_changed)
        layout.addWidget(self.incoherent_integration_cb)
        
        incoherent_window_layout = QHBoxLayout()
        incoherent_window_layout.addWidget(QLabel("  窗口大小:"))
        self.incoherent_integration_spin = QSpinBox()
        self.incoherent_integration_spin.setRange(3, 21)
        self.incoherent_integration_spin.setSingleStep(2)
        self.incoherent_integration_spin.setValue(5)
        self.incoherent_integration_spin.valueChanged.connect(self.on_setting_changed)
        incoherent_window_layout.addWidget(self.incoherent_integration_spin)
        layout.addLayout(incoherent_window_layout)
        
        # 异常点剔除累加
        self.outlier_rejection_cb = QCheckBox("异常点剔除累加")
        self.outlier_rejection_cb.stateChanged.connect(self.on_setting_changed)
        layout.addWidget(self.outlier_rejection_cb)
        
        outlier_window_layout = QHBoxLayout()
        outlier_window_layout.addWidget(QLabel("  窗口大小:"))
        self.outlier_rejection_spin = QSpinBox()
        self.outlier_rejection_spin.setRange(3, 21)
        self.outlier_rejection_spin.setSingleStep(2)
        self.outlier_rejection_spin.setValue(5)
        self.outlier_rejection_spin.valueChanged.connect(self.on_setting_changed)
        outlier_window_layout.addWidget(self.outlier_rejection_spin)
        layout.addLayout(outlier_window_layout)
        
        outlier_sigma_layout = QHBoxLayout()
        outlier_sigma_layout.addWidget(QLabel("  Sigma阈值:"))
        self.outlier_sigma_spin = QSpinBox()
        self.outlier_sigma_spin.setRange(1, 5)
        self.outlier_sigma_spin.setValue(2)
        self.outlier_sigma_spin.valueChanged.connect(self.on_setting_changed)
        outlier_sigma_layout.addWidget(self.outlier_sigma_spin)
        layout.addLayout(outlier_sigma_layout)
        
        # 微弱目标处理
        self.weak_target_cb = QCheckBox("微弱目标处理")
        self.weak_target_cb.stateChanged.connect(self.on_setting_changed)
        layout.addWidget(self.weak_target_cb)
        
        weak_target_window_layout = QHBoxLayout()
        weak_target_window_layout.addWidget(QLabel("  窗口大小:"))
        self.weak_target_spin = QSpinBox()
        self.weak_target_spin.setRange(3, 21)
        self.weak_target_spin.setSingleStep(2)
        self.weak_target_spin.setValue(7)
        self.weak_target_spin.valueChanged.connect(self.on_setting_changed)
        weak_target_window_layout.addWidget(self.weak_target_spin)
        layout.addLayout(weak_target_window_layout)
        
        group.setLayout(layout)
        return group
    
    def create_background_group(self):
        """创建背景处理组"""
        group = QGroupBox("背景处理")
        layout = QVBoxLayout()
        
        set_bg_btn = QPushButton("设置当前帧为背景")
        set_bg_btn.clicked.connect(self.set_background)
        layout.addWidget(set_bg_btn)
        
        self.subtract_bg_cb = QCheckBox("减背景")
        self.subtract_bg_cb.stateChanged.connect(self.on_setting_changed)
        layout.addWidget(self.subtract_bg_cb)
        
        clear_bg_btn = QPushButton("清除背景")
        clear_bg_btn.clicked.connect(self.clear_background)
        layout.addWidget(clear_bg_btn)
        
        group.setLayout(layout)
        return group
    
    def open_file(self):
        """打开 DatX 文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "打开 DatX 文件",
            "",
            "DatX Files (*.datx);;All Files (*)"
        )
        
        if file_path:
            try:
                self.status_bar.showMessage("正在加载文件...")
                self.raw_frames = self.reader.load(file_path)
                
                frame_count = self.reader.get_frame_count()
                self.frame_slider.setMaximum(frame_count - 1)
                self.frame_slider.setValue(0)
                self.current_frame_idx = 0
                
                self.status_bar.showMessage(
                    f"已加载: {Path(file_path).name} ({frame_count} 帧, {self.reader.width}×{self.reader.height})"
                )
                
                self.update_display()
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法加载文件:\n{str(e)}")
                self.status_bar.showMessage("加载失败")
    
    def save_frame(self):
        """保存当前帧"""
        if self.current_image is None:
            QMessageBox.warning(self, "警告", "没有可保存的图像")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存当前帧",
            "",
            "PNG Files (*.png);;TIFF Files (*.tiff);;All Files (*)"
        )
        
        if file_path:
            try:
                # 获取当前显示的图像（已经过处理和伪彩色映射）
                cv2.imwrite(file_path, cv2.cvtColor(self.current_image, cv2.COLOR_RGB2BGR))
                self.status_bar.showMessage(f"已保存: {Path(file_path).name}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法保存文件:\n{str(e)}")
    
    def on_frame_changed(self, value):
        """帧滑动条变化处理"""
        self.current_frame_idx = value
        self.update_display()
    
    def on_bit_mode_changed(self, text):
        """位深度模式变化处理"""
        if text == "8-bit":
            self.processor.bit_mode = 8
        else:
            self.processor.bit_mode = 14
        self.update_display()
    
    def on_setting_changed(self):
        """设置变化处理"""
        # 更新处理器参数 - 显示设置
        self.processor.enable_auto_contrast = self.auto_contrast_cb.isChecked()
        self.processor.enable_percentile_clipping = self.percentile_clipping_cb.isChecked()
        self.processor.low_percentile = float(self.low_percentile_spin.value())
        self.processor.high_percentile = float(self.high_percentile_spin.value())
        
        # 空域滤波
        self.processor.enable_gaussian = self.gaussian_cb.isChecked()
        self.processor.enable_median = self.median_cb.isChecked()
        self.processor.enable_bilateral = self.bilateral_cb.isChecked()
        
        self.processor.gaussian_kernel = self.gaussian_spin.value()
        self.processor.median_kernel = self.median_spin.value()
        
        # 时域滤波 - 基础
        self.processor.enable_temporal = self.temporal_cb.isChecked()
        self.processor.temporal_window = self.temporal_spin.value()
        
        # 时域滤波 - 高级
        self.processor.enable_temporal_median = self.temporal_median_cb.isChecked()
        self.processor.temporal_median_window = self.temporal_median_spin.value()
        
        self.processor.enable_incoherent_integration = self.incoherent_integration_cb.isChecked()
        self.processor.incoherent_integration_window = self.incoherent_integration_spin.value()
        
        self.processor.enable_outlier_rejection = self.outlier_rejection_cb.isChecked()
        self.processor.outlier_rejection_window = self.outlier_rejection_spin.value()
        self.processor.outlier_sigma = float(self.outlier_sigma_spin.value())
        
        self.processor.enable_weak_target_processing = self.weak_target_cb.isChecked()
        self.processor.weak_target_window = self.weak_target_spin.value()
        
        # 背景处理
        self.processor.enable_background_subtraction = self.subtract_bg_cb.isChecked()
        
        self.update_display()
    
    def set_background(self):
        """设置当前帧为背景"""
        if self.raw_frames is None:
            QMessageBox.warning(self, "警告", "请先加载文件")
            return
        
        current_frame = self.reader.get_frame(self.current_frame_idx)
        self.processor.set_background(current_frame)
        self.status_bar.showMessage(f"已设置帧 {self.current_frame_idx} 为背景")
    
    def clear_background(self):
        """清除背景"""
        self.processor.set_background(None)
        self.subtract_bg_cb.setChecked(False)
        self.status_bar.showMessage("已清除背景")
        self.update_display()
    
    def update_display(self):
        """更新图像显示"""
        if self.raw_frames is None:
            return
        
        try:
            # 获取原始帧
            raw_frame = self.reader.get_frame(self.current_frame_idx)
            
            # 应用处理管线
            processed = self.processor.process(
                raw_frame,
                all_frames=self.raw_frames,
                frame_idx=self.current_frame_idx
            )
            
            # 应用伪彩色映射
            colormap_name = self.colormap_combo.currentText()
            colored = self.colormap_converter.apply_colormap(processed, colormap_name)
            
            # 存储当前图像（用于保存）
            self.current_image = colored
            
            # 转换为 QPixmap 显示
            height, width, channel = colored.shape
            bytes_per_line = 3 * width
            q_image = QImage(colored.data, width, height, bytes_per_line, QImage.Format_RGB888)
            
            # 缩放显示
            pixmap = QPixmap.fromImage(q_image)
            scaled_pixmap = pixmap.scaled(
                self.image_label.width(),
                self.image_label.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
            
            # 更新帧标签
            frame_count = self.reader.get_frame_count()
            self.frame_label.setText(f"{self.current_frame_idx + 1} / {frame_count}")
            
        except Exception as e:
            print(f"显示更新错误: {e}")
            import traceback
            traceback.print_exc()

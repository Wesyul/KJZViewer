# 新增时域滤波功能说明

## 概述
为了解决用户在使用 KJZViewer 时遇到的**闪烁椒盐噪声**和**微弱目标不明显**的问题，本次更新在 `core/filters.py` 和 `core/image_processor.py` 中添加了四种新的时域滤波方法。

## 问题背景
用户在查看红外图像数据时遇到两个主要问题：
1. **闪烁的椒盐噪声**：噪声位置不固定，在不同帧的不同位置随机出现
2. **目标信号微弱**：有效信号淹没在背景噪声中，难以观察

## 新增功能

### 1. 时域中值滤波 (Temporal Median Filter)
**方法**: `ImageFilters.temporal_median(frames, current_idx, window=5)`

**原理**: 对同一像素位置取多帧的中值，闪烁噪声会被直接剔除（因为噪声是随机出现的异常值）

**适用场景**:
- 处理随机出现的椒盐噪声
- 需要保持边缘和细节的去噪场景

**参数说明**:
- `frames`: 所有帧数据 (n_frames, height, width)
- `current_idx`: 当前帧索引
- `window`: 滑动窗口大小（默认5，建议3-11）

**使用示例**:
```python
processor = ImageProcessor()
processor.enable_temporal_median = True
processor.temporal_median_window = 5
result = processor.process(frame, all_frames=frames, frame_idx=idx)
```

### 2. 非相干积累 (Incoherent Integration)
**方法**: `ImageFilters.incoherent_integration(frames, current_idx, window=5)`

**原理**: 对多帧幅度进行累加，可以提升 sqrt(N) 倍信噪比，增强微弱目标

**适用场景**:
- 增强微弱目标的可见度
- 提高信噪比
- 已经去噪的数据进一步增强

**参数说明**:
- `frames`: 所有帧数据 (n_frames, height, width)
- `current_idx`: 当前帧索引  
- `window`: 累加窗口大小（默认5，建议5-15）

**使用示例**:
```python
processor = ImageProcessor()
processor.enable_incoherent_integration = True
processor.incoherent_integration_window = 7
result = processor.process(frame, all_frames=frames, frame_idx=idx)
```

### 3. 异常点剔除累加 (Outlier-Rejected Integration)
**方法**: `ImageFilters.outlier_rejected_integration(frames, current_idx, window=5, sigma=2.0)`

**原理**: 去掉每个像素时间序列中的异常值（基于 sigma 剔除）后再累加，结合了去噪和增强效果

**适用场景**:
- 同时处理噪声和微弱目标
- 需要既去噪又增强的场景
- 替代分步处理的一步式解决方案

**参数说明**:
- `frames`: 所有帧数据 (n_frames, height, width)
- `current_idx`: 当前帧索引
- `window`: 滑动窗口大小（默认5，建议5-11）
- `sigma`: 异常值剔除阈值（默认2.0）
  - 1.0-1.5: 严格剔除（可能误删真实信号）
  - 2.0-2.5: 平衡（推荐）
  - 3.0+: 宽松剔除（保留更多数据）

**使用示例**:
```python
processor = ImageProcessor()
processor.enable_outlier_rejection = True
processor.outlier_rejection_window = 5
processor.outlier_sigma = 2.0
result = processor.process(frame, all_frames=frames, frame_idx=idx)
```

### 4. 微弱目标+闪烁噪声综合处理
**方法**: `ImageFilters.process_weak_target_with_flicker_noise(frames, current_idx, window=7)`

**原理**: 
1. 先用时域中值去除闪烁噪声
2. 再进行多帧累加增强目标

**适用场景**:
- 一键处理"闪烁噪声+微弱目标"场景
- 需要最佳处理效果的场合

**参数说明**:
- `frames`: 所有帧数据 (n_frames, height, width)
- `current_idx`: 当前帧索引
- `window`: 处理窗口大小（默认7，建议7-15）

**使用示例**:
```python
processor = ImageProcessor()
processor.enable_weak_target_processing = True
processor.weak_target_window = 7
result = processor.process(frame, all_frames=frames, frame_idx=idx)
```

## ImageProcessor 更新

### 新增开关参数
```python
processor.enable_temporal_median = False          # 时域中值滤波
processor.enable_incoherent_integration = False   # 非相干积累
processor.enable_outlier_rejection = False        # 异常点剔除累加
processor.enable_weak_target_processing = False   # 综合处理
```

### 新增配置参数
```python
processor.temporal_median_window = 5              # 时域中值窗口
processor.incoherent_integration_window = 5       # 非相干积累窗口
processor.outlier_rejection_window = 5            # 异常点剔除窗口
processor.outlier_sigma = 2.0                     # 异常值剔除阈值
processor.weak_target_window = 7                  # 综合处理窗口
```

## 处理顺序
在 `ImageProcessor.process()` 中，时域滤波的处理顺序为：

1. **组合处理优先**：如果启用 `enable_weak_target_processing`，直接使用组合方法
2. **去噪处理**：按优先级选择
   - `enable_outlier_rejection` > `enable_temporal_median` > `enable_temporal`
3. **增强处理**：如果启用 `enable_incoherent_integration`（且未使用异常点剔除），进行非相干积累

## 使用建议

### 场景1：主要是闪烁噪声
```python
processor.enable_temporal_median = True
processor.temporal_median_window = 5  # 中等窗口
```

### 场景2：主要是微弱目标
```python
processor.enable_incoherent_integration = True
processor.incoherent_integration_window = 9  # 较大窗口
```

### 场景3：闪烁噪声+微弱目标（推荐）
```python
# 方案A：使用组合处理（推荐）
processor.enable_weak_target_processing = True
processor.weak_target_window = 7

# 方案B：使用异常点剔除累加
processor.enable_outlier_rejection = True
processor.outlier_rejection_window = 5
processor.outlier_sigma = 2.0
```

### 场景4：自定义处理链
```python
# 先去噪，再增强
processor.enable_temporal_median = True
processor.temporal_median_window = 5
processor.enable_incoherent_integration = True
processor.incoherent_integration_window = 7
```

## 性能考虑

- **窗口大小**：窗口越大，处理效果越好，但计算时间越长
  - 小窗口 (3-5): 快速处理，适合实时预览
  - 中窗口 (5-9): 平衡效果和速度（推荐）
  - 大窗口 (9-15): 最佳效果，适合最终处理

- **计算复杂度**：
  - 时域中值: O(window × H × W)
  - 非相干积累: O(window × H × W)
  - 异常点剔除: O(window × H × W)
  - 综合处理: O(window² × H × W)（最慢但效果最好）

## 测试
所有新功能都经过了完整的单元测试，测试文件：`test_temporal_filters.py`

运行测试：
```bash
python test_temporal_filters.py
```

## 技术说明

### 时域中值滤波的有效性
闪烁椒盐噪声的特点是位置随机、时间上不连续。在时间序列中，噪声点是异常值，而真实信号相对稳定。中值滤波能够稳健地剔除这些异常值，保留真实信号。

### 非相干积累的信噪比提升
假设噪声是独立的高斯噪声，信号在多帧中相对稳定：
- 信号累加：S_total = N × S（线性增长）
- 噪声累加：N_total ≈ sqrt(N) × σ（平方根增长）
- 信噪比提升：SNR_improvement = sqrt(N)

例如，9帧累加可提升约3倍信噪比。

### 异常点剔除的鲁棒性
使用 sigma 剔除方法，对每个像素的时间序列：
1. 计算均值 μ 和标准差 σ
2. 剔除超出 [μ - k×σ, μ + k×σ] 范围的值
3. 对剩余值进行累加

这种方法既能去除噪声（异常值），又能累加真实信号，实现一步式处理。

## 注意事项

1. **帧数要求**：所有方法都需要多帧数据，建议至少有 window 大小的帧数
2. **边界处理**：对于靠近起始/结束的帧，实际使用的窗口可能小于设定值
3. **参数调整**：建议先用默认参数测试，再根据实际效果调整
4. **组合使用**：避免同时启用多个时域滤波方法，选择最适合的一种即可

## 代码示例

### 完整处理流程
```python
from core.datx_reader import DatxReader
from core.image_processor import ImageProcessor

# 1. 加载数据
reader = DatxReader()
frames = reader.load('data.datx')

# 2. 配置处理器
processor = ImageProcessor()
processor.bit_mode = 8
processor.enable_auto_contrast = True

# 3. 启用时域滤波
processor.enable_weak_target_processing = True
processor.weak_target_window = 7

# 4. 处理单帧
for i in range(reader.get_frame_count()):
    frame = reader.get_frame(i)
    processed = processor.process(frame, all_frames=frames, frame_idx=i)
    # ... 显示或保存结果
```

## 兼容性
- 完全兼容现有的 ImageProcessor 框架
- 不影响现有功能
- 可与空域滤波、背景减除等功能组合使用
- 遵循现有代码风格和命名规范

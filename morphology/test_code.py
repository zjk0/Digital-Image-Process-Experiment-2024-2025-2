import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

# 假设图像为二维数组
img = np.random.randint(0, 256, (5, 5), dtype=np.uint8)

# 得到所有 3x3 局部窗口
windows = sliding_window_view(img, (3, 3))

# 示例：每个 3x3 区域取最小值，作为中心输出
result = np.min(windows, axis=(-2, -1))

windows_1 = windows[:, :] * 2

print(windows_1)
print(result)
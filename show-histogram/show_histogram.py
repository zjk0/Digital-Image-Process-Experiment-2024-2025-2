import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from PIL import Image
from PIL import ImageTk
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

# 创建基本的界面
root = tk.Tk()
root.title("数字图像处理实验三：直方图绘制")  # 设置界面标题
frame = ttk.Frame(root, padding = 10)
frame.grid()

'''
@brief 获取灰度直方图分布
@param image: Image对象
'''
def gray_histogram (image):
    all_gray = np.arange(256)  # 所有灰度值
    image_array = np.array(image.getdata())  # 获取图像数据并转化为数组
    gray_distribution = np.zeros(256)  # 用于统计每个灰度值出现的频率

    # 遍历所有灰度值
    for i in range(256):
        gray_distribution[i] = np.count_nonzero(image_array == i) / (image.size[0] * image.size[1])  # 获取图像中每个灰度值出现的频率

    # 绘制直方图
    figure.clear()  # 清除图窗中的图像
    histogram = figure.add_subplot()
    histogram.bar(all_gray, gray_distribution, width = 0.6)
    histogram.set_title("gray histogram")
    histogram.set_xlabel("gray value")
    histogram.set_ylabel("frequence")
    canvas.draw()
  
'''
@brief 获取RGB三个通道的直方图分布
@param image: Image对象
'''
def color_histogram (image):
    all_pixel_value = np.arange(256)  # 所有像素值
    image_array = np.array(image.getdata())  # 获取图像数据并转化为数组
    color_distribution = np.zeros((3, 256))  # 用于分别统计每个RGB值出现的频率

    # 遍历所有RGB值
    for i in range(3):
        for j in range(256):
            color_distribution[i, j] = np.count_nonzero(image_array[:, i] == j) / (image.size[0] * image.size[1])  # 分别获取图像中每个RGB值出现的频率

    # 绘制直方图
    figure.clear()  # 清除图窗中的图像
    histogram = figure.add_subplot(1, 3, 1)
    histogram.bar(all_pixel_value, color_distribution[0, :], width = 0.6)
    histogram.set_title("red pixel histogram")
    histogram.set_xlabel("pixel value")
    histogram.set_ylabel("frequence")
    histogram = figure.add_subplot(1, 3, 2)
    histogram.bar(all_pixel_value, color_distribution[1, :], width = 0.6)
    histogram.set_title("green pixel histogram")
    histogram.set_xlabel("pixel value")
    histogram.set_ylabel("frequence")
    histogram = figure.add_subplot(1, 3, 3)
    histogram.bar(all_pixel_value, color_distribution[2, :], width = 0.6)
    histogram.set_title("blue pixel histogram")
    histogram.set_xlabel("pixel value")
    histogram.set_ylabel("frequence")
    canvas.draw()

'''
@brief 打开文件
@param none
'''
def open_file ():
    global image_tk
    file_path = fd.askopenfilename()  # 获取文件路径
    image = Image.open(file_path)  # 通过图片路径打开图片
    image_tk = ImageTk.PhotoImage(image)  # 将图像转化为tkinter可用的PhotoImage对象

    # 显示图片
    image_label = ttk.Label(frame, image = image_tk)
    image_label.grid(row = 3, column = 0)

    # 判断显示什么类型图像的直方图
    if image.mode == "L":
        gray_histogram(image)
    elif image.mode == "RGB":
        color_histogram(image)

# 提示语
tip_1 = ttk.Label(frame, text = "如果打开的图像为灰度图像，则会显示灰度分布直方图")
tip_1.grid(row = 0, column = 0)
tip_2 = ttk.Label(frame, text = "如果打开的图像为彩色图像，则会分别显示红绿蓝三个通道的分布直方图")
tip_2.grid(row = 1, column = 0)

# 创建“打开文件”按键
open_file_button = ttk.Button(frame, text = "打开文件并绘制直方图", command = open_file)  # 将按键的回调定位到open_file函数
open_file_button.grid(row = 2, column = 0)

# 创建“quit”按键
quit_button = ttk.Button(frame, text = "quit", command = root.destroy)
quit_button.grid(row = 6, column = 0)

# 创建图窗
figure = Figure(figsize = (18, 5), dpi = 100)

# 创建嵌入tkinter界面的图窗部件
canvas = FigureCanvasTkAgg(figure, frame)
canvas.draw()  # 确保图窗中的图像可以更新
canvas.get_tk_widget().grid(row = 4, column = 0)

# 创建图窗工具栏
toolbar = NavigationToolbar2Tk(canvas, frame, pack_toolbar = False)
toolbar.update()  # 确保工具栏能够更新图像
toolbar.grid(row = 5, column = 0)

root.mainloop()
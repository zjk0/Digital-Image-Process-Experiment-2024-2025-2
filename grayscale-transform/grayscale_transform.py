import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from PIL import Image
from PIL import ImageTk
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

'''
@brief 获取灰度图像数据
@param image: PIL的Image类
@return width: 图像的宽度
@return height: 图像的高度
@return image_array: 图像对应的二维数组
'''
def get_image_data (image):
    (width, height) = image.size  # 获取图像的宽和高
    image_array = np.array(image.getdata())  # 获取图像的像素数据并转化为数组
    image_array = image_array.reshape((height, width))  # 转化为二维数组
    return width, height, image_array

'''
@brief 绘制图像的直方图
@param image: PIL的Image类
'''
def show_histogram (image_array, histogram, canvas):
    all_gray = np.arange(256)
    gray_distribution = np.zeros(256)
    for i in range(256):
        gray_distribution[i] = np.count_nonzero(image_array == i)  # 获取每个像素值出现的个数

    # 绘制直方图
    histogram.clear()  # 清除原图表
    histogram.bar(all_gray, gray_distribution, width = 0.6)
    histogram.set_title("gray histogram")
    histogram.set_xlabel("gray value")
    histogram.set_ylabel("num")
    canvas.draw()

'''
@brief 在图形界面上显示图片
@param image_array: 图像像素值数组
'''
def show_transformed_image (image_array):
    global transformed_image_tk
    transformed_image = Image.fromarray(image_array)
    transformed_image_tk = ImageTk.PhotoImage(transformed_image)
    transformed_image_label.config(image = transformed_image_tk)

'''
@brief “打开文件”按键的回调函数，打开文件选择界面，并对文件进行相应操作
@param none
'''
def file_operation ():
    global origin_image, origin_image_tk
    file_path = fd.askopenfilename()  # 获取文件路径
    origin_image = Image.open(file_path)  # 打开文件，得到Image类的对象

    # 显示原图像
    origin_image_tk = ImageTk.PhotoImage(origin_image)  # 转换为tkinter可解析的PhotoImage类的对象
    origin_image_label.config(image = origin_image_tk)  # 显示图像

    # 显示原图像的直方图
    _, _, origin_image_array = get_image_data(origin_image)
    show_histogram(origin_image_array, histogram_origin, canvas_origin)

class GrayscaleTransform:
    '''
    @brief 灰度图像反转变换
    @param image: PIL的Image类
    '''
    def reverse (self, image):
        # 获取图像数据
        width, height, image_array = get_image_data(image)

        # 灰度反转
        array_255 = np.ones((height, width)) * 255
        image_array = array_255 - image_array

        # 显示反转后的图像
        show_transformed_image(image_array)

        # 绘制反转后的直方图
        show_histogram(image_array, histogram_transformed, canvas_transformed)

    '''
    @brief 灰度图像对数变换
    @param image: PIL的Image类
    '''
    def log_transform (self, image):
        pass

    '''
    @brief 灰度图像幂次变换
    @param image: PIL的Image类
    '''
    def pow_transform (self, image):
        pass

    '''
    @brief 灰度直方图均衡化
    @param image: PIL的Image类
    '''
    def histogram_equalization (self, image):
        pass

if __name__ == '__main__':
    # 创建灰度变换对象
    grayscale_transform = GrayscaleTransform()

    # 创建基本界面
    root = tk.Tk()
    root.title("数字图像处理实验四：灰度变换")
    frame = ttk.Frame(root, padding = 10)
    frame.grid()

    # 创建“打开文件”按键
    open_file_button = ttk.Button(frame, text = "打开文件", command = file_operation)  # 将按键的回调定位到open_file函数
    open_file_button.grid(row = 0, column = 0)

    # 创建灰度变换选项按键
    reverse_button = ttk.Button(frame, text = "灰度反转", command = lambda: grayscale_transform.reverse(origin_image))
    reverse_button.grid(row = 1, column = 0)
    log_button = ttk.Button(frame, text = "对数变换", command = lambda: grayscale_transform.log_transform(origin_image))
    log_button.grid(row = 1, column = 1)
    pow_button = ttk.Button(frame, text = "幂次变换", command = lambda: grayscale_transform.pow_transform(origin_image))
    pow_button.grid(row = 2, column = 0)
    equalization_button = ttk.Button(frame, text = "直方图均衡化", command = lambda: grayscale_transform.histogram_equalization(origin_image))
    equalization_button.grid(row = 2, column = 1)

    # 用于显示原始图像和转换后的图像
    origin_image_label = ttk.Label(frame)  # 显示原始图像
    origin_image_label.grid(row = 3, column = 0)
    transformed_image_label = ttk.Label(frame)  # 显示转换后的图像
    transformed_image_label.grid(row = 5, column = 0)

    # 创建图窗
    figure_origin = Figure(figsize = (5, 5), dpi = 100)  # 显示原始图像直方图
    histogram_origin = figure_origin.add_subplot()  # 添加绘图区域
    figure_transformed = Figure(figsize = (5, 5), dpi = 100)  # 显示转换后的图像的直方图
    histogram_transformed = figure_transformed.add_subplot()  # 添加绘图区域

    # 创建嵌入tkinter界面的图窗部件
    canvas_origin = FigureCanvasTkAgg(figure_origin, frame)  # 原始图像直方图
    canvas_origin.draw()  # 确保图窗中的图像可以更新
    canvas_origin.get_tk_widget().grid(row = 3, column = 1)
    canvas_transformed = FigureCanvasTkAgg(figure_transformed, frame)  # 转换后的图像的直方图
    canvas_transformed.draw()  # 确保图窗中的图像可以更新
    canvas_transformed.get_tk_widget().grid(row = 5, column = 1)

    # 创建图窗工具栏
    toolbar_origin = NavigationToolbar2Tk(canvas_origin, frame, pack_toolbar = False)
    toolbar_origin.update()  # 确保工具栏能够更新图像
    toolbar_origin.grid(row = 4, column = 1)
    toolbar_transformed = NavigationToolbar2Tk(canvas_transformed, frame, pack_toolbar = False)
    toolbar_transformed.update()  # 确保工具栏能够更新图像
    toolbar_transformed.grid(row = 6, column = 1)

    # 创建“quit”按键
    quit_button = ttk.Button(frame, text = "quit", command = root.destroy)
    quit_button.grid(row = 7, column = 0)

    root.mainloop()
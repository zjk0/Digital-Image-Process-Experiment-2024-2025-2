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
    histogram.bar(all_gray, gray_distribution, width = 0.8)
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

    # 转换后的图像和其直方图清空，准备用于显示新选择的图像的转换后的图像和直方图
    transformed_image_label.config(image = "")
    histogram_transformed.clear()

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
        # 获取图像数据
        _, _, image_array = get_image_data(image)

        # 获取输入数据
        log_base = float(log_base_entry.get())
        coef = float(log_coef_entry.get())

        # 灰度对数变换
        image_array = coef * (np.log1p(image_array) / np.log(log_base))  # 使用对数换底公式进行灰度对数变换
        # image_array = np.clip(image_array, None, 255)  # 将数组的值限制在[0, 255]
        image_array = 255 / (np.max(image_array)) * image_array  # 将数组的值归一化到[0, 255]
        image_array = image_array.astype(np.uint8)  # 转换为无符号8位整数

        # 显示对数变换后的图像
        show_transformed_image(image_array)

        # 绘制对数变换后的图像的直方图
        show_histogram(image_array, histogram_transformed, canvas_transformed)

    '''
    @brief 灰度图像幂次变换
    @param image: PIL的Image类
    '''
    def pow_transform (self, image):
        # 获取图像数据
        _, _, image_array = get_image_data(image)

        # 获取输入数据
        pow_num = float(pow_num_entry.get())
        coef = float(pow_coef_entry.get())

        # 灰度幂次变换
        image_array = coef * (np.power(image_array, pow_num))  # 进行灰度幂次变换
        # image_array = np.clip(image_array, None, 255)  # 将数组的值限制在[0, 255]
        image_array = 255 / (np.max(image_array)) * image_array  # 将数组的值归一化到[0, 255]
        image_array = image_array.astype(np.uint8)  # 转换为无符号8位整数
        
        # 显示幂次变换后的图像
        show_transformed_image(image_array)

        # 绘制幂次变换后的图像的直方图
        show_histogram(image_array, histogram_transformed, canvas_transformed)

    '''
    @brief 灰度直方图均衡化
    @param image: PIL的Image类
    '''
    def histogram_equalization (self, image):
        # 获取图像数据
        width, height, image_array = get_image_data(image)
        pixel_num = width * height  # 计算像素数总数
        
        # 计算累积分布函数
        grayscale_cdf = np.zeros(256)  # 初始化累积分布函数数组
        for i in range(256):  # 计算每一像素值处的函数值
            grayscale_cdf[i] = np.count_nonzero(image_array == i) if i == 0 else grayscale_cdf[i - 1] + np.count_nonzero(image_array == i)

        # 直方图均衡化
        image_array = (255 / pixel_num) * grayscale_cdf[image_array]
        image_array = image_array.astype(np.uint8)  # 转换为无符号8位整数

        # 显示幂次变换后的图像
        show_transformed_image(image_array)

        # 绘制幂次变换后的图像的直方图
        show_histogram(image_array, histogram_transformed, canvas_transformed)

if __name__ == '__main__':
    # 创建灰度变换对象
    grayscale_transform = GrayscaleTransform()

    # 创建基本界面
    root = tk.Tk()
    root.title("数字图像处理实验四：灰度变换")
    root.grid_rowconfigure(0, weight = 1)
    root.grid_columnconfigure(0, weight = 1)
    canvas = tk.Canvas(root)  # 向root放入一个canvas
    frame = ttk.Frame(canvas, padding = 10)  # 将frame放入canvas中，便于使用滚动条上下移动
    frame.bind("<Configure>", lambda func: canvas.configure(scrollregion = canvas.bbox("all")))  # 与<Configure>事件绑定，使canvas能够适应界面大小的变化
    frame.grid()

    # 创建滚动条
    scrollbar_1 = ttk.Scrollbar(root, orient = "vertical", command = canvas.yview)
    scrollbar_2 = ttk.Scrollbar(root, orient = "horizontal", command = canvas.xview)

    # canvas与frame、滚动条关联
    canvas.create_window((0, 0), window = frame, anchor="nw")
    canvas.configure(yscrollcommand = scrollbar_1.set)
    canvas.configure(xscrollcommand = scrollbar_2.set)

    # canvas和滚动条设置位置
    canvas.grid(row = 0, column = 0, sticky = "nsew")
    scrollbar_1.grid(row = 0, column = 1, sticky = "ns")
    scrollbar_2.grid(row = 1, column = 0, sticky = "ew")

    # 创建“打开文件”按键
    open_file_button = ttk.Button(frame, text = "打开文件", command = file_operation)  # 将按键的回调定位到open_file函数
    open_file_button.grid(row = 0, column = 0)

    # 创建灰度变换选项按键
    reverse_button = ttk.Button(frame, text = "灰度反转", command = lambda: grayscale_transform.reverse(origin_image))
    reverse_button.grid(row = 1, column = 0)
    equalization_button = ttk.Button(frame, text = "直方图均衡化", command = lambda: grayscale_transform.histogram_equalization(origin_image))
    equalization_button.grid(row = 1, column = 1)
    pow_button = ttk.Button(frame, text = "幂次变换", command = lambda: grayscale_transform.pow_transform(origin_image))
    pow_button.grid(row = 2, column = 0)
    log_button = ttk.Button(frame, text = "对数变换", command = lambda: grayscale_transform.log_transform(origin_image))
    log_button.grid(row = 3, column = 0)

    # 创建幂次变换参数输入框
    pow_param_entry_frame = ttk.Frame(frame)
    pow_param_entry_frame.grid(row = 2, column = 1)
    pow_num_entry_tip = ttk.Label(pow_param_entry_frame, text = "请输入幂次变换的幂次：")
    pow_num_entry_tip.grid(row = 0, column = 0)
    pow_num_entry = ttk.Entry(pow_param_entry_frame)
    pow_num_entry.grid(row = 0, column = 1)
    pow_coef_entry_tip = ttk.Label(pow_param_entry_frame, text = "请输入幂次变换的系数：")
    pow_coef_entry_tip.grid(row = 1, column = 0)
    pow_coef_entry = ttk.Entry(pow_param_entry_frame)
    pow_coef_entry.grid(row = 1, column = 1)

    # 创建对数变换参数输入框
    log_param_entry_frame = ttk.Frame(frame)
    log_param_entry_frame.grid(row = 3, column = 1)
    log_base_entry_tip = ttk.Label(log_param_entry_frame, text = "请输入对数变换的底数：")
    log_base_entry_tip.grid(row = 0, column = 0)
    log_base_entry = ttk.Entry(log_param_entry_frame)
    log_base_entry.grid(row = 0, column = 1)
    log_coef_entry_tip = ttk.Label(log_param_entry_frame, text = "请输入对数变换的系数：")
    log_coef_entry_tip.grid(row = 1, column = 0)
    log_coef_entry = ttk.Entry(log_param_entry_frame)
    log_coef_entry.grid(row = 1, column = 1)
    
    # 用于显示原始图像和转换后的图像
    origin_image_label = ttk.Label(frame)  # 显示原始图像
    origin_image_label.grid(row = 4, column = 0)
    transformed_image_label = ttk.Label(frame)  # 显示转换后的图像
    transformed_image_label.grid(row = 6, column = 0)

    # 创建图窗
    figure_origin = Figure(figsize = (5, 5), dpi = 100)  # 显示原始图像直方图
    histogram_origin = figure_origin.add_subplot()  # 添加绘图区域
    figure_transformed = Figure(figsize = (5, 5), dpi = 100)  # 显示转换后的图像的直方图
    histogram_transformed = figure_transformed.add_subplot()  # 添加绘图区域

    # 创建嵌入tkinter界面的图窗部件
    canvas_origin = FigureCanvasTkAgg(figure_origin, frame)  # 原始图像直方图
    canvas_origin.draw()  # 确保图窗中的图像可以更新
    canvas_origin.get_tk_widget().grid(row = 4, column = 1)
    canvas_transformed = FigureCanvasTkAgg(figure_transformed, frame)  # 转换后的图像的直方图
    canvas_transformed.draw()  # 确保图窗中的图像可以更新
    canvas_transformed.get_tk_widget().grid(row = 6, column = 1)

    # 创建图窗工具栏
    toolbar_origin = NavigationToolbar2Tk(canvas_origin, frame, pack_toolbar = False)
    toolbar_origin.update()  # 确保工具栏能够更新图像
    toolbar_origin.grid(row = 5, column = 1)
    toolbar_transformed = NavigationToolbar2Tk(canvas_transformed, frame, pack_toolbar = False)
    toolbar_transformed.update()  # 确保工具栏能够更新图像
    toolbar_transformed.grid(row = 7, column = 1)

    # 创建“quit”按键
    quit_button = ttk.Button(frame, text = "quit", command = root.destroy)
    quit_button.grid(row = 0, column = 1)

    root.mainloop()
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from PIL import Image
from PIL import ImageTk
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import struct
import math

'''
@brief RGB空间映射到HSV空间
@param image: PIL的Image类
@return image: HSV空间的图像的Image类
'''
def RGB_to_HSV (image):
    image = image.convert("HSV")
    return image

'''
@brief HSV空间映射到RGB空间
@param image: PIL的Image类
@return image: RGB空间的图像的Image类
'''
def HSV_to_RGB (image):
    image = image.convert("RGB")
    return image

'''
@brief 获取图像数组
@param image: PIL的Image类对象
@return height: 图像的高（行数）
@return width: 图像的宽（列数）
@return image_array: 图像对应的数组
'''
def get_image_data (image):
    (width, height) = image.size  # 获取图像的宽和高
    image_array = np.array(image)  # 获取图像的像素数据并转化为数组
    return height, width, image_array

'''
@brief 显示分割后的图像
@param image_array: 图像数组
'''
def show_seg_image (image_array):
    global seg_image_tk

    # 转换
    image = Image.fromarray(np.uint8(image_array))
    seg_image_tk = ImageTk.PhotoImage(image)

    # 显示分割后的图片
    seg_image_label.config(image = seg_image_tk)

'''
@brief 计算图像归一化直方图
@param image_array: 图像数组
@return histogram: 图像归一化直方图
'''
def get_histogram (image_array):
    # 获取图像行数、列数
    rows = image_array.shape[0]
    columns = image_array.shape[1]

    # 计算归一化直方图
    if len(image_array.shape) == 2:
        histogram = np.zeros(256)
        for i in range(256):
            histogram[i] = np.count_nonzero(image_array == i) / (rows * columns)
    elif len(image_array.shape) == 3:
        histogram = np.zeros((3, 256))
        for i in range(3):
            for j in range(256):
                histogram[i, j] = np.count_nonzero(image_array[:, i] == j) / (rows * columns)
        
    return histogram

'''
@brief 获取由otsu算法得到的图像分割阈值
@param image_array: 图像数组
@param min_grayscale: 算法作用范围的下界
@param max_grayscale: 算法作用范围的上界
@return otsu_threshold: 通过otsu算法得到的最佳阈值点
'''
def get_otsu_threshold (image_array, min_grayscale, max_grayscale):
    # 初始化
    prob1 = 0  # 前景概率
    prob2 = 0  # 背景概率
    mean1 = 0  # 前景均值
    mean2 = 0  # 背景均值
    var = 0  # 类间方差
    otsu_threshold = 0  # ostu算法阈值

    # 获取归一化直方图
    histogram = get_histogram(image_array)

    # 计算算法作用范围的总概率
    prob = np.sum(histogram[min_grayscale : max_grayscale + 1])

    # 遍历所有灰度值
    for i in range(min_grayscale, max_grayscale + 1):
        # 计算前景概率、背景概率、前景均值和背景均值
        if i == min_grayscale:
            prob1 = histogram[min_grayscale] / prob
            prob2 = np.sum(histogram[min_grayscale : max_grayscale + 1]) / prob
            mean1 = 0
            mean2 = np.average(np.arange(min_grayscale, max_grayscale + 1), weights = histogram[min_grayscale : max_grayscale + 1] / prob)
        else:
            mean1 = (prob1 * mean1 + i * histogram[i] / prob) / (prob1 + histogram[i] / prob)
            if prob2 - histogram[i] / prob == 0:
                mean2 = 0
            else:
                mean2 = (prob2 * mean2 - i * histogram[i] / prob) / (prob2 - histogram[i] / prob)
            prob1 = prob1 + histogram[i] / prob
            prob2 = prob2 - histogram[i] / prob

        # 计算类间方差
        if prob1 * prob2 * ((mean1 - mean2) ** 2) > var:
            var = prob1 * prob2 * ((mean1 - mean2) ** 2)
            otsu_threshold = i

    return otsu_threshold

'''
@brief 分割CT图像
@param none
'''
def threshold_segmentation ():
    global origin_image
    _, _, image_array = get_image_data(origin_image)  # 获取图像数组
    threshold = get_otsu_threshold(image_array, 0, 255)  # 第一次获取ostu算法的阈值
    threshold = get_otsu_threshold(image_array, threshold, 255)  # 第二次获取ostu算法的阈值
    image_array[image_array < threshold] = 0  # 小于该阈值的像素值置为0
    image_array[image_array >= threshold] = 255  # 大于或等于该阈值的像素值置为255
    show_seg_image(image_array)  # 显示分割后的图像
    seg_image_tip.config(text = "分割后的图像")

'''
@brief 提取彩色图像指定颜色区域
@param nnoe
'''
def threshold_color_segmentation ():
    global origin_image
    hsv_image = RGB_to_HSV(origin_image)

    _, _, hsv_image_array = get_image_data(hsv_image)
    seg_color = None

    popup = tk.Toplevel(root)
    popup.title("选择颜色")
    popup.grid()
    red_button = ttk.Button(popup, text = "红色")
    red_button.grid(row = 0, column = 0)
    blue_button = ttk.Button(popup, text = "蓝色")
    blue_button.grid(row = 0, column = 1)
    yellow_button = ttk.Button(popup, text = "黄色")
    yellow_button.grid(row = 0, column = 2)
    green_button = ttk.Button(popup, text = "绿色")
    green_button.grid(row = 0, column = 3)

    '''
    @brief 点击了“红色”按键
    @param none
    '''
    def click_red_button ():
        nonlocal seg_color
        seg_color = "red"
        bool_var.set(True)
        popup.destroy()

    '''
    @brief 点击了“蓝色”按键
    @param none
    '''
    def click_blue_button ():
        nonlocal seg_color
        seg_color = "blue"
        bool_var.set(True)
        popup.destroy()

    '''
    @brief 点击了“黄色”按键
    @param none
    '''
    def click_yellow_button ():
        nonlocal seg_color
        seg_color = "yellow"
        bool_var.set(True)
        popup.destroy()

    '''
    @brief 点击了“绿色”按键
    @param none
    '''
    def click_green_button ():
        nonlocal seg_color
        seg_color = "green"
        bool_var.set(True)
        popup.destroy()

    red_button.config(command = click_red_button)
    blue_button.config(command = click_blue_button)
    yellow_button.config(command = click_yellow_button)
    green_button.config(command = click_green_button)

    # 等待平移参数输入完毕
    root.wait_variable(bool_var)
    bool_var.set(False)  # 复位bool_var

    bool_index = None
    if seg_color == "red":
        bool_index = (((hsv_image_array[:, :, 0] >= 0) & (hsv_image_array[:, :, 0] <= 10)) | \
                     ((hsv_image_array[:, :, 0] >= 240) & (hsv_image_array[:, :, 0] <= 255))) & \
                     ((hsv_image_array[:, :, 1] >= 200) & (hsv_image_array[:, :, 1] <= 255)) & \
                     ((hsv_image_array[:, :, 2] >= 200) & (hsv_image_array[:, :, 2] <= 255))
    elif seg_color == "blue":
        bool_index = ((hsv_image_array[:, :, 0] >= 140) & (hsv_image_array[:, :, 0] <= 170)) & \
                     ((hsv_image_array[:, :, 1] >= 200) & (hsv_image_array[:, :, 1] <= 255)) & \
                     ((hsv_image_array[:, :, 2] >= 100) & (hsv_image_array[:, :, 2] <= 255))
    elif seg_color == "yellow":
        bool_index = ((hsv_image_array[:, :, 0] >= 25) & (hsv_image_array[:, :, 0] <= 45)) & \
                     ((hsv_image_array[:, :, 1] >= 200) & (hsv_image_array[:, :, 1] <= 255)) & \
                     ((hsv_image_array[:, :, 2] >= 200) & (hsv_image_array[:, :, 2] <= 255))
    elif seg_color == "green":
        bool_index = ((hsv_image_array[:, :, 0] >= 60) & (hsv_image_array[:, :, 0] <= 105)) & \
                     ((hsv_image_array[:, :, 1] >= 100) & (hsv_image_array[:, :, 1] <= 255)) & \
                     ((hsv_image_array[:, :, 2] >= 100) & (hsv_image_array[:, :, 2] <= 255))
        
    hsv_image_array[:, :, 2][~bool_index] = 0

    hsv_image = Image.fromarray(hsv_image_array, mode = "HSV")
    rgb_image = HSV_to_RGB(hsv_image)
    _, _, rgb_image_array = get_image_data(rgb_image)
    show_seg_image(rgb_image_array)
    seg_image_tip.config(text = "分割后的图像")

'''
@brief “打开文件”按键的回调函数，打开文件选择界面，并对文件进行相应操作
@param none
'''
def file_operation ():
    global origin_image, origin_image_tk
    file_path = fd.askopenfilename()  # 获取文件路径
    
    origin_image = Image.open(file_path)  # 打开图像得到Image类对象
    origin_image_tk = ImageTk.PhotoImage(origin_image)  # 转化为PhotoImage类对象
    origin_image_label.config(image = origin_image_tk)  # 显示原始图像
    origin_image_tip.config(text = "原图像")  # 显示原始图像标注
    seg_image_label.config(image = "")  # 清空分隔后的图像
    seg_image_tip.config(text = "")  # 清空分割后的图像的标注
    
if __name__ == '__main__':
    # 创建基本界面
    root = tk.Tk()
    root.title("数字图像处理实验六：图像分割")  # 设置界面标题
    root.grid()
    root.grid_columnconfigure(0, weight = 1)  # root的第一列会适应界面大小的改变
    root.grid_rowconfigure(0, weight = 1)  # root的第一行会适应界面大小的改变

    # 创建一个画布，画布可以被滚动条控制
    canvas = tk.Canvas(root)
    canvas.grid(row = 0, column = 0, sticky = "nsew")  # canvas会填充整个界面

    # 创建滚动条
    scrollbar_1 = ttk.Scrollbar(root, orient = "vertical", command = canvas.yview)
    scrollbar_1.grid(row = 0, column = 1, sticky = "ns")  # 纵轴方向填充
    scrollbar_2 = ttk.Scrollbar(root, orient = "horizontal", command = canvas.xview)
    scrollbar_2.grid(row = 1, column = 0, sticky = "ew")  # 横轴方向填充

    # canvas与滚动条关联
    canvas.config(yscrollcommand = scrollbar_1.set)
    canvas.config(xscrollcommand = scrollbar_2.set)

    # 创建Frame容器，用于存放各种子容器
    frame = ttk.Frame(canvas, padding = 10)
    frame.grid(row = 0, column = 0)
    canvas.create_window((0, 0), window = frame, anchor = "nw")  # 将frame嵌入canvas
    frame.bind("<Configure>", lambda event: canvas.configure(scrollregion = canvas.bbox("all")))  # 使滚动条适应frame

    # 创建存放按键的Frame容器
    button_frame = ttk.Frame(frame, padding = 10)
    button_frame.grid(row = 0, column = 0)

    # 创建“打开文件”按键
    open_file_button = ttk.Button(button_frame, text = "打开文件", command = file_operation)
    open_file_button.grid(row = 0, column = 0, columnspan = 5)

    # 创建“退出”按键
    quit_button = ttk.Button(button_frame, text = "退出", command = root.destroy)
    quit_button.grid(row = 3, column = 0)

    # 创建功能按键
    seg_ct_image_button = ttk.Button(button_frame, text = "分割CT图像", command = threshold_segmentation)
    seg_ct_image_button.grid(row = 1, column = 0)
    seg_colorful_image_button = ttk.Button(button_frame, text = "提取彩色图像指定颜色区域", command = threshold_color_segmentation)
    seg_colorful_image_button.grid(row = 2, column = 0)

    # 创建图像标签
    origin_image_label = ttk.Label(frame)
    origin_image_label.grid(row = 1, column = 0)
    seg_image_label = ttk.Label(frame)
    seg_image_label.grid(row = 1, column = 1)

    # 创建图像标注
    origin_image_tip = ttk.Label(frame)
    origin_image_tip.grid(row = 2, column = 0)
    seg_image_tip = ttk.Label(frame)
    seg_image_tip.grid(row = 2, column = 1)

    # 创建一个布尔变量，判断“确定”按键是否按下
    bool_var = tk.BooleanVar()

    root.mainloop()
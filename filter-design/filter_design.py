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
@brief 读取raw文件
@param file_name: raw文件路径
@return raw_array: raw文件图像数组
'''
def read_raw (file_name):
    # 获取raw文件表示的图片的数据
    raw_file = open(file_name, "rb")  # 打开文件，以只读、二进制的方式打开
    raw_width = struct.unpack("i", raw_file.read(4))[0]  # 获取raw文件表示的图片的宽度
    raw_height = struct.unpack("i", raw_file.read(4))[0]  # 获取raw文件表示的图片的高度
    raw_data = struct.unpack(f"{raw_width * raw_height}B", raw_file.read())  # 获取raw文件表示的图片的数组
    raw_file.close()  # 关闭文件

    # 将获取到的数组转换为二维数组
    raw_array = np.array(raw_data).reshape((raw_height, raw_width))

    return raw_array

'''
@brief 显示通过滤波器后的图像
@param image_array: 图像数组
'''
def show_filter_image (image_array):
    global filter_image_tk

    # 转换
    image = Image.fromarray(np.uint8(image_array))
    filter_image_tk = ImageTk.PhotoImage(image)

    # 显示分割后的图片
    filter_image_label.config(image = filter_image_tk)

'''
@brief 滑动滑动条的回调函数
@param kernel_size: 核函数大小
@return none
'''
def update_kernel_size_and_image (kernel_size):
    img_filter.set_kernel_size(int(kernel_size))
    filter_image(img_filter.filter_type)

'''
@brief 重置核函数大小
@param none
@return none
'''
def reset_kernel_size_scale ():
    kernel_size_scale.set(init_kernel_size)

class ImgFilter:
    def __init__ (self, kernel_size, image_array):
        self.kernel_size = kernel_size  # 核函数大小
        self.image_array = image_array  # 原始图像矩阵
        self.filter_type = None  # 使用的滤波器类型

    '''
    @brief 设置核函数大小
    @param kernel_size: 核函数大小
    @return none
    '''
    def set_kernel_size (self, kernel_size):
        self.kernel_size = kernel_size

    '''
    @brief 扩展数组，用于二维卷积
    @param none
    @return 扩展后的数组
    '''
    def expand_array (self):
        center_to_bound = int((self.kernel_size - 1) / 2)
        rows = self.image_array.shape[0]
        columns = self.image_array.shape[1]
        new_rows = rows + self.kernel_size - 1
        new_columns = columns + self.kernel_size - 1

        expanded_array = np.zeros((new_rows, new_columns))
        expanded_array[center_to_bound : new_rows - center_to_bound, center_to_bound : new_columns - center_to_bound] = np.copy(self.image_array)
        expanded_array[center_to_bound : new_rows - center_to_bound, 0 : center_to_bound] = np.copy(self.image_array[:, columns - center_to_bound : columns])
        expanded_array[center_to_bound : new_rows - center_to_bound, new_columns - center_to_bound : new_columns] = np.copy(self.image_array[:, 0 : center_to_bound])
        expanded_array[0 : center_to_bound, center_to_bound : new_columns - center_to_bound] = np.copy(self.image_array[rows - center_to_bound : rows, :])
        expanded_array[new_rows - center_to_bound : new_rows, center_to_bound : new_columns - center_to_bound] = np.copy(self.image_array[0 : center_to_bound, :])
        expanded_array[0 : center_to_bound, 0 : center_to_bound] = np.copy(self.image_array[rows - center_to_bound : rows, columns - center_to_bound : columns])
        expanded_array[0 : center_to_bound, new_columns - center_to_bound : new_columns] = np.copy(self.image_array[rows - center_to_bound : rows, 0 : center_to_bound])
        expanded_array[new_rows - center_to_bound : new_rows, 0 : center_to_bound] = np.copy(self.image_array[0 : center_to_bound, columns - center_to_bound : columns])
        expanded_array[new_rows - center_to_bound : new_rows, new_columns - center_to_bound : new_columns] = np.copy(self.image_array[0 : center_to_bound, 0 : center_to_bound])

        return expanded_array

    '''
    @brief 计算二维卷积
    @param kernel_matrix: 核函数矩阵
    @return 二维卷积结果
    '''
    def convolution_2d (self, kernel_matrix):
        # 核函数边缘与核函数中心之间的距离
        center_to_bound = int((self.kernel_size - 1) / 2)

        # 扩展数组
        expanded_array = self.expand_array()

        # 扩展后的数组的行数和列数
        rows = expanded_array.shape[0]
        columns = expanded_array.shape[1]

        # 初始化卷积结果
        conv_result = np.zeros((rows - self.kernel_size + 1, columns - self.kernel_size + 1))

        # 计算二维卷积
        for i in range(center_to_bound, rows - center_to_bound):
            for j in range(center_to_bound, columns - center_to_bound):
                conv_result[i - center_to_bound, j - center_to_bound] = np.sum(np.multiply(expanded_array[i - center_to_bound : i + center_to_bound + 1, j - center_to_bound : j + center_to_bound + 1], kernel_matrix))

        return conv_result

    '''
    @brief 均值滤波
    @param none
    @return 均值滤波结果
    '''
    def img_mean_filter (self):
        self.filter_type = "mean"
        mean_coef = 1 / (self.kernel_size ** 2)
        mean_kernel = np.ones((self.kernel_size, self.kernel_size)) * mean_coef  # 获取均值核函数
        return self.convolution_2d(mean_kernel)

    '''
    @brief 中值滤波
    @param none
    @return 中值滤波结果
    '''
    def img_median_filter (self):
        self.filter_type = "median"

        # 核函数边缘与核函数中心之间的距离
        center_to_bound = int((self.kernel_size - 1) / 2)

        # 扩展数组
        expanded_array = self.expand_array()

        # 扩展后的数组的行数和列数
        rows = expanded_array.shape[0]
        columns = expanded_array.shape[1]

        # 初始化滤波结果
        filter_result = np.zeros((rows - self.kernel_size + 1, columns - self.kernel_size + 1))

        # 中值滤波过程
        for i in range(center_to_bound, rows - center_to_bound):
            for j in range(center_to_bound, columns - center_to_bound):
                sorted_array = np.sort(expanded_array[i - center_to_bound : i + center_to_bound + 1, j - center_to_bound : j + center_to_bound + 1], axis = None)
                index = int((self.kernel_size ** 2 - 1) / 2)
                filter_result[i - center_to_bound, j - center_to_bound] = sorted_array[index]

        return filter_result

    '''
    @brief 获取高斯滤波的核函数
    @param std_var: 高斯函数标准差
    @return 高斯核函数
    '''
    def create_Gaussian_kernel (self, std_var):
        # 初始化高斯核函数
        gaussian_kernel = np.zeros((self.kernel_size, self.kernel_size))

        # 计算核函数中心点
        cx = int((self.kernel_size - 1) / 2)
        cy = cx

        # 计算高斯核函数
        for i in range(self.kernel_size):
            for j in range(self.kernel_size):
                x = i - cx
                y = j - cy
                gaussian_kernel[i, j] = (1 / (2 * np.pi * std_var ** 2)) * np.exp(-(x ** 2 + y ** 2) / (2 * std_var ** 2))
        
        gaussian_kernel = gaussian_kernel / np.sum(gaussian_kernel)

        return gaussian_kernel

    '''
    @brief 高斯滤波
    @param std_var: 标准差
    @return 高斯滤波结果
    '''
    def img_Gaussian_filter (self, std_var):
        self.filter_type = "Gaussian"
        gaussian_kernel = self.create_Gaussian_kernel(std_var)  # 获取高斯核函数
        return self.convolution_2d(gaussian_kernel)

    '''
    @brief 获取Sobel核函数
    @param none
    @return x方向和y方向的Sobel核函数
    '''
    def create_Sobel_kernel (self):
        n = self.kernel_size - 1
        sobel_kernel_x = np.zeros((self.kernel_size, self.kernel_size))

        # 计算组合数
        temp_array = np.zeros(self.kernel_size)
        for i in range(self.kernel_size):
            temp_array[i] = math.comb(n, i)

        # 计算x方向的Sobel核函数
        for i in range(self.kernel_size):
            if i < int((self.kernel_size - 1) / 2):
                sobel_kernel_x[:, i] = -(i + 1) * temp_array
            elif i > int((self.kernel_size - 1) / 2):
                sobel_kernel_x[:, i] = (self.kernel_size - i) * temp_array

        # y方向的Sobel核函数是x方向的核函数的转置
        sobel_kernel_y = sobel_kernel_x.T

        return sobel_kernel_x, sobel_kernel_y

    '''
    @brief Sobel滤波
    @param none
    @return Sobel滤波结果
    '''
    def img_Sobel_filter (self):
        self.filter_type = "Sobel"
        sobel_kernel_x, sobel_kernel_y = self.create_Sobel_kernel()  # 获取核函数
        grad_x = self.convolution_2d(sobel_kernel_x)
        grad_y = self.convolution_2d(sobel_kernel_y)
        sobel_result = (abs(grad_x) + abs(grad_y)) / np.max(abs(grad_x) + abs(grad_y)) * 255  # 使用相加而不是平方和开根号，从而减少运算
        sobel_result = np.uint8(sobel_result)
        return sobel_result

    '''
    @brief 获取Laplace核函数
    @param none
    @return 大小为3*3、5*5、7*7、9*9、11*11之中的其中一个的Laplace核函数
    '''
    def create_Laplace_kernel (self):
        laplace_kernel = None

        if self.kernel_size == 3:
            laplace_kernel = np.array([
                [0, -1, 0],
                [-1, 4, -1],
                [0, -1, 0]
            ])
        elif self.kernel_size == 5:
            laplace_kernel = np.array([
                [0, 0, -1, 0, 0],
                [0, -1, -2, -1, 0],
                [-1, -2, 16, -2, -1],
                [0, -1, -2, -1, 0],
                [0, 0, -1, 0, 0]
            ])
        elif self.kernel_size == 7:
            laplace_kernel = np.array([
                [ 0,  0,  0, -1,  0,  0,  0],
                [ 0,  0, -1, -2, -1,  0,  0],
                [ 0, -1, -2, -3, -2, -1,  0],
                [-1, -2, -3, 40, -3, -2, -1],
                [ 0, -1, -2, -3, -2, -1,  0],
                [ 0,  0, -1, -2, -1,  0,  0],
                [ 0,  0,  0, -1,  0,  0,  0]
            ])
        elif self.kernel_size == 9:
            laplace_kernel = np.array([
                [ 0,  0,  0,  0, -1,  0,  0,  0,  0],
                [ 0,  0,  0, -1, -2, -1,  0,  0,  0],
                [ 0,  0, -1, -2, -3, -2, -1,  0,  0],
                [ 0, -1, -2, -3, -4, -3, -2, -1,  0],
                [-1, -2, -3, -4, 80, -4, -3, -2, -1],
                [ 0, -1, -2, -3, -4, -3, -2, -1,  0],
                [ 0,  0, -1, -2, -3, -2, -1,  0,  0],
                [ 0,  0,  0, -1, -2, -1,  0,  0,  0],
                [ 0,  0,  0,  0, -1,  0,  0,  0,  0]
            ])
        elif self.kernel_size == 11:
            laplace_kernel = np.array([
                [ 0,  0,  0,  0,  0, -1,  0,  0,  0,  0,  0],
                [ 0,  0,  0,  0, -1, -2, -1,  0,  0,  0,  0],
                [ 0,  0,  0, -1, -2, -3, -2, -1,  0,  0,  0],
                [ 0,  0, -1, -2, -3, -4, -3, -2, -1,  0,  0],
                [ 0, -1, -2, -3, -4, -5, -4, -3, -2, -1,  0],
                [-1, -2, -3, -4, -5, 140, -5, -4, -3, -2, -1],
                [ 0, -1, -2, -3, -4, -5, -4, -3, -2, -1,  0],
                [ 0,  0, -1, -2, -3, -4, -3, -2, -1,  0,  0],
                [ 0,  0,  0, -1, -2, -3, -2, -1,  0,  0,  0],
                [ 0,  0,  0,  0, -1, -2, -1,  0,  0,  0,  0],
                [ 0,  0,  0,  0,  0, -1,  0,  0,  0,  0,  0]
            ])

        return laplace_kernel

    '''
    @brief Laplace滤波
    @param none
    @return Laplace滤波结果
    '''
    def img_Laplace_filter (self):
        self.filter_type = "Laplace"
        laplace_kernel = self.create_Laplace_kernel()  # 获取Laplace核函数
        laplace_result = self.convolution_2d(laplace_kernel)  # 二维卷积
        laplace_result = abs(laplace_result) / np.max(abs(laplace_result)) * 255  # 归一化
        laplace_result = np.uint8(laplace_result)
        return laplace_result       

def gaussian_filter_image ():
    global std_var

    def click_certain_button ():
        global std_var
        std_var = float(entry_area.get())  # 获取标准差
        bool_var.set(True)
        popup.destroy()

    # 创建弹窗
    popup = tk.Toplevel(root)
    popup.title("输入参数")
    popup.grid()
    entry_tip = ttk.Label(popup, text = "标准差：")
    entry_tip.grid(row = 0, column = 0)
    entry_area = ttk.Entry(popup)
    entry_area.grid(row = 0, column = 1)
    certain_button = ttk.Button(popup, text = "确定", command = click_certain_button)
    certain_button.grid(row = 1, column = 0, columnspan = 2)

    # 等待标准差输入完毕
    root.wait_variable(bool_var)
    bool_var.set(False)  # 复位bool_var

    filter_image_array = img_filter.img_Gaussian_filter(std_var)

    # 显示滑动条
    kernel_size_scale.config(to = 45)
    min_scale_label.config(text = f"{kernel_size_scale.cget("from")}")
    max_scale_label.config(text = f"{kernel_size_scale.cget("to")}")
    scale_frame.grid(row = 3, column = 1)

    # 显示图像和标注
    show_filter_image(filter_image_array)
    filter_image_tip.config(text = f"{img_filter.filter_type}滤波后的图像，核函数大小为{img_filter.kernel_size}")

def highpass_filter_image (filter_type):
    reset_kernel_size_scale()

    if filter_type == "Sobel":
        filter_image_array = img_filter.img_Sobel_filter()
        kernel_size_scale.config(to = 11)
    elif filter_type == "Laplace":
        filter_image_array = img_filter.img_Laplace_filter()
        kernel_size_scale.config(to = 11)

    # 显示滑动条
    min_scale_label.config(text = f"{kernel_size_scale.cget("from")}")
    max_scale_label.config(text = f"{kernel_size_scale.cget("to")}")
    scale_frame.grid(row = 3, column = 1)

    # 显示图像和标注
    show_filter_image(filter_image_array)
    filter_image_tip.config(text = f"{img_filter.filter_type}滤波后的图像，核函数大小为{img_filter.kernel_size}")

def filter_image (filter_str):
    # 判断是哪种滤波器
    if filter_str == "mean":
        filter_image_array = img_filter.img_mean_filter()
        kernel_size_scale.config(to = 45)
    elif filter_str == "median":
        filter_image_array = img_filter.img_median_filter()
        kernel_size_scale.config(to = 45)
    elif filter_str == "Gaussian":
        filter_image_array = img_filter.img_Gaussian_filter(std_var)
        kernel_size_scale.config(to = 45)
    elif filter_str == "Sobel":
        filter_image_array = img_filter.img_Sobel_filter()
        kernel_size_scale.config(to = 11)
    elif filter_str == "Laplace":
        filter_image_array = img_filter.img_Laplace_filter()
        kernel_size_scale.config(to = 11)

    # 显示滑动条
    min_scale_label.config(text = f"{kernel_size_scale.cget("from")}")
    max_scale_label.config(text = f"{kernel_size_scale.cget("to")}")
    scale_frame.grid(row = 3, column = 1)

    # 显示图像和标注
    show_filter_image(filter_image_array)
    filter_image_tip.config(text = f"{img_filter.filter_type}滤波后的图像，核函数大小为{img_filter.kernel_size}")

def file_operation ():
    global origin_image_tk, img_filter

    # 获取文件路径
    file_path = fd.askopenfilename()

    # 获取文件格式
    file_format = []
    for i in reversed(range(len(file_path))):
        if file_path[i] == '.':  # 由于只需要文件格式，所以遇到'.'就退出
            break

        file_format.append(file_path[i])

    file_format.reverse()  # 列表反转
    file_format_str = "".join(file_format)  # 转换为字符串

    # 判断文件格式并得到Image对象和图像数组
    if file_format_str == "raw":
        image_array = read_raw(file_path)
        image = Image.fromarray(image_array)
    else:
        image = Image.open(file_path)
        _, _, image_array = get_image_data(image)

    # 创建图像滤波器类对象
    img_filter = ImgFilter(kernel_size = init_kernel_size, image_array = image_array)

    # 转换为tkinter能解析的PhotoImage对象   
    origin_image_tk = ImageTk.PhotoImage(image)

    # 显示图像
    origin_image_label.config(image = origin_image_tk)
    origin_image_tip.config(text = "原图像")
    filter_image_label.config(image = "")
    filter_image_tip.config(text = "")
    scale_frame.grid_forget()
    reset_kernel_size_scale()

if __name__ == '__main__':
    # 初始核函数大小
    init_kernel_size = 3

    # 创建基本界面
    root = tk.Tk()
    root.title("数字图像处理实验七：滤波器设计")  # 设置界面标题
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
    quit_button.grid(row = 2, column = 0, columnspan = 5)

    # 创建功能按键
    mean_filter_button = ttk.Button(button_frame, text = "均值滤波", command = lambda: filter_image("mean"))
    mean_filter_button.grid(row = 1, column = 0)
    median_filter_button = ttk.Button(button_frame, text = "中值滤波", command = lambda: filter_image("median"))
    median_filter_button.grid(row = 1, column = 1)
    Gaussian_filter_button = ttk.Button(button_frame, text = "高斯滤波", command = gaussian_filter_image)
    Gaussian_filter_button.grid(row = 1, column = 2)
    Sobel_filter_button = ttk.Button(button_frame, text = "索贝尔滤波", command = lambda: highpass_filter_image("Sobel"))
    Sobel_filter_button.grid(row = 1, column = 3)
    Laplace_filter_button = ttk.Button(button_frame, text = "拉普拉斯滤波", command = lambda: highpass_filter_image("Laplace"))
    Laplace_filter_button.grid(row = 1, column = 4)

    # 创建存放滑动条的Frame容器
    scale_frame = ttk.Frame(frame, padding = 10)
    # scale_frame.grid(row = 3, column = 1)

    # 创建滑动条以调整核函数大小
    kernel_size_scale = tk.Scale(scale_frame, from_ = 3, orient = "horizontal", length = 150, command = update_kernel_size_and_image, resolution = 2)
    kernel_size_scale.set(init_kernel_size)  # 设置滑动条的初始值
    kernel_size_scale.grid(row = 0, column = 1)
    min_scale_label = ttk.Label(scale_frame)
    min_scale_label.grid(row = 0, column = 0)
    max_scale_label = ttk.Label(scale_frame)
    max_scale_label.grid(row = 0, column = 2)


    # 创建图像标签
    origin_image_label = ttk.Label(frame)
    origin_image_label.grid(row = 1, column = 0)
    filter_image_label = ttk.Label(frame)
    filter_image_label.grid(row = 1, column = 1)

    # 创建图像标注
    origin_image_tip = ttk.Label(frame)
    origin_image_tip.grid(row = 2, column = 0)
    filter_image_tip = ttk.Label(frame)
    filter_image_tip.grid(row = 2, column = 1)

    # 创建一个布尔变量，判断“确定”按键是否按下
    bool_var = tk.BooleanVar()

    root.mainloop()
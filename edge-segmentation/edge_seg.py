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
from filter_design import ImgFilter
import cv2 as cv

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
@brief 显示分割后的图像
@param image_array: 图像数组
'''
def show_edge_image (image_array):
    global edge_image_tk

    # 转换
    image = Image.fromarray(np.uint8(image_array))
    edge_image_tk = ImageTk.PhotoImage(image)

    # 显示分割后的图片
    edge_image_label.config(image = edge_image_tk)

def Sobel_Segmentation (kernel_size):
    global edge_method
    edge_method = "sobel"
    img_filter.set_kernel_size(kernel_size)
    seg_image_array = img_filter.img_Sobel_filter()
    canny_upper_thres_tip.grid_forget()
    canny_upper_thres_scale.grid_forget()
    canny_lower_thres_tip.grid_forget()
    canny_lower_thres_scale.grid_forget()
    show_edge_image(seg_image_array)
    edge_image_tip.config(text = f"{edge_method}边缘检测")
    scale_frame.grid(row = 3, column = 1)

def Canny_Segmentation (lower_thres, upper_thres, sobel_size):
    global edge_method
    edge_method = "canny"
    canny_image_array = cv.Canny(image_array, lower_thres, upper_thres, apertureSize = sobel_size)
    canny_upper_thres_tip.grid(row = 2, column = 0)
    canny_upper_thres_scale.grid(row = 2, column = 1)
    canny_lower_thres_tip.grid(row = 1, column = 0)
    canny_lower_thres_scale.grid(row = 1, column = 1)
    show_edge_image(canny_image_array)
    edge_image_tip.config(text = f"{edge_method}边缘检测")
    scale_frame.grid(row = 3, column = 1)

def update_sobel_kernel_size_and_image (kernel_size):
    global current_sobel_size, current_upper_thres, current_lower_thres, edge_method
    current_sobel_size = int(kernel_size)

    if edge_method == "sobel":
        Sobel_Segmentation(current_sobel_size)
    elif edge_method == "canny":
        Canny_Segmentation(current_lower_thres, current_upper_thres, current_sobel_size)

def update_canny_lower_thres_and_image (lower_thres):
    global current_sobel_size, current_upper_thres, current_lower_thres
    current_lower_thres = int(lower_thres)
    Canny_Segmentation(current_lower_thres, current_upper_thres, current_sobel_size)

def update_canny_upper_thres_and_image (upper_thres):
    global current_sobel_size, current_upper_thres, current_lower_thres
    current_upper_thres = int(upper_thres)
    Canny_Segmentation(current_lower_thres, current_upper_thres, current_sobel_size)

def file_operation ():
    global origin_image_tk, img_filter, image_array

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
    edge_image_label.config(image = "")
    edge_image_tip.config(text = "")
    scale_frame.grid_forget()

if __name__ == '__main__':
    # 初始化参数
    init_kernel_size = 3
    init_lower_thres = 50
    init_upper_thres = 150
    edge_method = None
    current_lower_thres = init_lower_thres
    current_upper_thres = init_upper_thres
    current_sobel_size = init_kernel_size

    # 创建基本界面
    root = tk.Tk()
    root.title("数字图像处理实验八：基于边缘的图像分割")  # 设置界面标题
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
    open_file_button.grid(row = 0, column = 0, columnspan = 2)

    # 创建“退出”按键
    quit_button = ttk.Button(button_frame, text = "退出", command = root.destroy)
    quit_button.grid(row = 2, column = 0, columnspan = 2)

    # 创建功能按键
    sobel_button = ttk.Button(button_frame, text = "Sobel边缘检测", command = lambda: Sobel_Segmentation(current_sobel_size))
    sobel_button.grid(row = 1, column = 0)
    canny_button = ttk.Button(button_frame, text = "Canny边缘检测", command = lambda: Canny_Segmentation(current_lower_thres, current_upper_thres, current_sobel_size))
    canny_button.grid(row = 1, column = 1)

    # 创建存放滑动条的Frame容器
    scale_frame = ttk.Frame(frame, padding = 10)
    # scale_frame.grid(row = 3, column = 1)

    # 创建滑动条
    sobel_kernel_size_tip = ttk.Label(scale_frame, text = "sobel算子大小")
    sobel_kernel_size_tip.grid(row = 0, column = 0)
    sobel_kernel_size_scale = tk.Scale(scale_frame, from_ = 3, to = 7, orient = "horizontal", length = 150, command = update_sobel_kernel_size_and_image, resolution = 2)
    sobel_kernel_size_scale.set(init_kernel_size)
    sobel_kernel_size_scale.grid(row = 0, column = 1)
    canny_lower_thres_tip = ttk.Label(scale_frame, text = "canny小阈值")
    canny_lower_thres_tip.grid(row = 1, column = 0)
    canny_lower_thres_scale = tk.Scale(scale_frame, from_ = 0, to = 255, orient = "horizontal", length = 150, command = update_canny_lower_thres_and_image)
    canny_lower_thres_scale.set(init_lower_thres)
    canny_lower_thres_scale.grid(row = 1, column = 1)
    canny_upper_thres_tip = ttk.Label(scale_frame, text = "canny大阈值")
    canny_upper_thres_tip.grid(row = 2, column = 0)
    canny_upper_thres_scale = tk.Scale(scale_frame, from_ = 0, to = 255, orient = "horizontal", length = 150, command = update_canny_upper_thres_and_image)
    canny_upper_thres_scale.set(init_upper_thres)
    canny_upper_thres_scale.grid(row = 2, column = 1)

    # 创建图像标签
    origin_image_label = ttk.Label(frame)
    origin_image_label.grid(row = 1, column = 0)
    edge_image_label = ttk.Label(frame)
    edge_image_label.grid(row = 1, column = 1)

    # 创建图像标注
    origin_image_tip = ttk.Label(frame)
    origin_image_tip.grid(row = 2, column = 0)
    edge_image_tip = ttk.Label(frame)
    edge_image_tip.grid(row = 2, column = 1)

    # 创建一个布尔变量，判断“确定”按键是否按下
    bool_var = tk.BooleanVar()

    root.mainloop()
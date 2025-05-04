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
from numpy.lib.stride_tricks import sliding_window_view

np.random.seed(100)

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
@brief 显示转换后的图像
@param image_array: 图像数组
'''
def show_transform_image (image_array):
    global transform_image_tk

    # 转换
    image = Image.fromarray(np.uint8(image_array))
    transform_image_tk = ImageTk.PhotoImage(image)

    # 显示分割后的图片
    transform_image_label.config(image = transform_image_tk)

def kmeans_segmentation (image_array, k):
    # 得到图像行数和列数
    rows = image_array.shape[0]
    columns = image_array.shape[1]
    
    # 在图像中随机选取k个点，作为最初的类中心
    label_centers_row = np.random.randint(0, rows, size = k)
    label_centers_column = np.random.randint(0, columns, size = k)
    label_centers = image_array[label_centers_row, label_centers_column]
    label_centers = label_centers.astype(np.float64)

    # 初始化类别数组
    last_labels = np.full((rows, columns), -1)  # 记录上一时刻的类别
    labels = np.zeros((rows, columns))

    while not np.array_equal(last_labels, labels):
        distance_list = []
        
        # 更新last_labels
        last_labels = np.copy(labels)

        # 计算每个像素点到类中心的距离
        for label_center in label_centers:
            if image_array.ndim == 2:  # 灰度图像
                distance = np.sqrt((image_array - label_center) ** 2)
            elif image_array.ndim == 3:  # RGB图像
                distance = np.sqrt(np.sum((image_array - label_center) ** 2, axis = -1))

            distance_list.append(distance)

        # 计算类别
        distances = np.stack(distance_list, axis = 0)
        labels = np.argmin(distances, axis = 0)
        labels = labels + 1

        # 更新类中心
        for label in range(1, k + 1):
            values = image_array[labels == label]
            if values.size == 0:
                if image_array.ndim == 2:
                    label_centers[label - 1] = np.random.randint(0, 256)
                elif image_array.ndim == 3:
                    label_centers[label - 1] = np.random.randint(0, 256, size = 3)
            else:
                if image_array.ndim == 2:  # 灰度图像
                    label_centers[label - 1] = values.mean()
                elif image_array.ndim == 3:  # RGB图像
                    label_centers[label - 1] = values.mean(axis = 0)

    return labels

def image_kmeans_segmentation ():
    global k
    result = np.copy(image_array)

    # k均值
    labels = kmeans_segmentation(image_array, k)

    for i in range(k):
        if image_array.ndim == 2:  # 灰度图像
            grayscale = int(i / (k - 1) * 255)
            result[labels == i + 1] = grayscale
        elif image_array.ndim == 3:  # RGB图像
            rgb_value = np.random.randint(0, 256, size = 3)
            result[labels == i + 1] = rgb_value

    show_transform_image(result)
    transform_image_tip.config(text = "k均值分割")
    scale_frame.grid(row = 3, column = 1)

def update_kmeans (k_):
    global k
    k = int(k_)
    image_kmeans_segmentation()

def file_operation ():
    global origin_image_tk, image_array

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

    # 转换为tkinter能解析的PhotoImage对象   
    origin_image_tk = ImageTk.PhotoImage(image)

    # 显示图像
    origin_image_label.config(image = origin_image_tk)
    origin_image_tip.config(text = "原图像")
    transform_image_label.config(image = "")
    transform_image_tip.config(text = "")
    scale_frame.grid_forget()

if __name__ == "__main__":
    # 初始化
    k = 2

    # 创建基本界面
    root = tk.Tk()
    root.title("数字图像处理实验十: 基于机器学习的图像分割")  # 设置界面标题
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
    open_file_button.grid(row = 0, column = 0)

    # 创建功能按键
    kmeans_button = ttk.Button(button_frame, text = "k均值分割", command = image_kmeans_segmentation)
    kmeans_button.grid(row = 1, column = 0)

    # 创建“退出”按键
    quit_button = ttk.Button(button_frame, text = "退出", command = root.destroy)
    quit_button.grid(row = 2, column = 0, columnspan = 4)

    # 创建图像标签
    origin_image_label = ttk.Label(frame)
    origin_image_label.grid(row = 1, column = 0)
    transform_image_label = ttk.Label(frame)
    transform_image_label.grid(row = 1, column = 1)

    # 创建图像标注
    origin_image_tip = ttk.Label(frame)
    origin_image_tip.grid(row = 2, column = 0)
    transform_image_tip = ttk.Label(frame)
    transform_image_tip.grid(row = 2, column = 1)

    # 创建存放滑动条的Frame容器
    scale_frame = ttk.Frame(frame, padding = 10)
    # scale_frame.grid(row = 3, column = 1)

    # 创建滑动条
    kmeas_scale = tk.Scale(scale_frame, from_ = 2, to = 30, orient = "horizontal", length = 150, command = update_kmeans)
    kmeas_scale.grid(row = 0, column = 0)
    kmeas_scale.set(k)

    root.mainloop()
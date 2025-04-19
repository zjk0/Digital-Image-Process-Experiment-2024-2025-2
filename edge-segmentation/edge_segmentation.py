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

def non_max_limit (image_array, grad_x, grad_y):
    pass

def double_threshold (image_array, lower_thres, upper_thres):
    rows = image_array.shape[0]
    columns = image_array.shape[1]

    result = np.zeros((rows, columns, 2))

    strong_edge_index = np.where(image_array > upper_thres)
    weak_edge_index = np.where((image_array >= lower_thres) & (image_array <= upper_thres))
    not_edge_index = np.where(image_array < lower_thres)

    result[strong_edge_index[0], strong_edge_index[1], 0] = image_array[strong_edge_index[0], strong_edge_index[1]]
    result[strong_edge_index[0], strong_edge_index[1], 1] = 2
    result[weak_edge_index[0], weak_edge_index[1], 0] = image_array[weak_edge_index[0], weak_edge_index[1]]
    result[weak_edge_index[0], weak_edge_index[1], 1] = 1
    result[not_edge_index[0], not_edge_index[1], 0] = 0
    result[not_edge_index[0], not_edge_index[1], 1] = 0

    return result

def check_connection (image_array):
    rows = image_array.shape[0]
    columns = image_array.shape[1]

    weak_edge_index = np.where(image_array[:, :, 1] == 1)

    for i, j in zip(weak_edge_index[0], weak_edge_index[1]):
        pass

def Canny_Segmentation ():
    gaussian_std = None
    gaussian_size = None
    sobel_size = None
    lower_thres = None
    upper_thres = None

    popup = tk.Toplevel(root)
    popup.title("输入参数")
    popup.grid()
    entry_tip_1 = ttk.Label(popup, text = "高斯滤波器标准差: ")
    entry_tip_1.grid(row = 0, column = 0)
    entry_area_1 = ttk.Entry(popup)
    entry_area_1.grid(row = 0, column = 1)
    entry_tip_2 = ttk.Label(popup, text = "高斯滤波器核函数大小: ")
    entry_tip_2.grid(row = 1, column = 0)
    entry_area_2 = ttk.Entry(popup)
    entry_area_2.grid(row = 1, column = 1)
    entry_tip_3 = ttk.Label(popup, text = "Sobel算子大小: ")
    entry_tip_3.grid(row = 2, column = 0)
    entry_area_3 = ttk.Entry(popup)
    entry_area_3.grid(row = 2, column = 1)
    entry_tip_4 = ttk.Label(popup, text = "小阈值: ")
    entry_tip_4.grid(row = 3, column = 0)
    entry_area_4 = ttk.Entry(popup)
    entry_area_4.grid(row = 3, column = 1)
    entry_tip_5 = ttk.Label(popup, text = "大阈值: ")
    entry_tip_5.grid(row = 4, column = 0)
    entry_area_5 = ttk.Entry(popup)
    entry_area_5.grid(row = 4, column = 1)

    '''
    @brief 确定参数已经输入完毕并获取旋转角度
    @param none
    '''
    def click_certain_button ():
        nonlocal gaussian_std, gaussian_size, sobel_size, lower_thres, upper_thres
        gaussian_std = float(entry_area_1.get())
        gaussian_size = int(entry_area_1.get())
        sobel_size = int(entry_area_1.get())
        lower_thres = int(entry_area_1.get())
        upper_thres = int(entry_area_1.get())
        bool_var.set(True)
        popup.destroy()

    certain_button = ttk.Button(popup, text = "确定", command = click_certain_button)
    certain_button.grid(row = 5, column = 0, columnspan = 2)

    # 等待旋转角度输入完毕
    root.wait_variable(bool_var)
    bool_var.set(False)  # 复位bool_var

    img_filter.set_kernel_size(gaussian_size)
    gaussian_filtered_image_array = img_filter.img_Gaussian_filter(gaussian_std)
    sobel_filter = ImgFilter(kernel_size = sobel_size, image_array = gaussian_filtered_image_array)
    grad_x, grad_y, sobel_filtered_image_array = sobel_filter.img_Sobel_filter()

    pass

def Sobel_Segmentation ():
    pass

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
    edge_image_label.config(image = "")
    edge_image_tip.config(text = "")

if __name__ == '__main__':
    # 初始核函数大小
    init_kernel_size = 3

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
    sobel_button = ttk.Button(button_frame, text = "Sobel边缘检测", command = Sobel_Segmentation)
    sobel_button.grid(row = 1, column = 0)
    canny_button = ttk.Button(button_frame, text = "Canny边缘检测", command = Canny_Segmentation)
    canny_button.grid(row = 1, column = 1)

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
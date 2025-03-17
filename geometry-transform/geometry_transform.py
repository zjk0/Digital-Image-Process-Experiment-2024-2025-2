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

''' 
@brief 读取raw文件
@param file_name: raw文件路径
'''
def read_raw (file_name):
    # 获取raw文件表示的图片的数据
    raw_file = open(file_name, "rb")  # 打开文件，以只读、二进制的方式打开
    raw_width = struct.unpack("i", raw_file.read(4))[0]  # 获取raw文件表示的图片的宽度
    raw_height = struct.unpack("i", raw_file.read(4))[0]  # 获取raw文件表示的图片的高度
    raw_data = struct.unpack(f"{raw_width * raw_height}B", raw_file.read())  # 获取raw文件表示的图片的数组
    raw_file.close()  # 关闭文件

    # 将获取到的数组转换为二维数组
    raw_array = np.array(raw_data).reshape(raw_height, raw_width)

    return raw_array

'''
@brief 图像绕其中心逆时针旋转90度
@param none
'''
def image_transpose ():
    pass

'''
@brief 图像绕其中心旋转
@param angle: 旋转的角度，单位为度，正数表示逆时针旋转，负数表示顺时针旋转
'''
def image_rotate (angle):
    pass

'''
@brief 图像平移
@param x_length: 在横轴方向上平移的长度，正负表示往正方向或负方向移动
@param y_length: 在纵轴方向上平移的长度，正负表示往正方向或负方向移动
'''
def image_translate (x_length, y_length):
    pass

'''
@brief 图像放大
@param zoom_in_coef: 放大倍数，需要大于一
'''
def image_zoom_in ():
    pass

'''
@brief 图像缩小
@param zoom_out_coef: 缩小倍数，需要大于一
'''
def image_zoom_out ():
    pass

'''
@brief 输入旋转角度
'''
def click_rotate_button ():
    pass

def click_translate_button ():
    pass

def click_zoom_in_button ():
    pass

def click_zoom_out_button ():
    pass

'''
@brief “打开文件”按键的回调函数，打开文件选择界面，并对文件进行相应操作
@param none
'''
def file_operation ():
    pass

if __name__ == '__main__':
    # 创建基本界面
    root = tk.Tk()
    root.title("数字图像处理实验五：几何变换")  # 设置界面标题
    root.grid()  # 使用grid工具来管理root布局
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

    # 创建按键Frame容器
    button_frame = ttk.Frame(canvas, padding = 10)
    button_frame.grid(row = 0, column = 0)  # 使用grid工具来管理button_frame布局
    canvas.create_window((0, 0), window = button_frame, anchor = "nw")
    button_frame.bind("<Configure>", lambda event: canvas.configure(scrollregion = canvas.bbox("all")))  # 使滚动条适应button_frame

    # 创建“打开文件”按键
    open_file_button = ttk.Button(button_frame, text = "打开文件", command = file_operation)
    open_file_button.grid(row = 0, column = 0, columnspan = 5)

    # 创建“退出”按键
    quit_button = ttk.Button(button_frame, text = "退出", command = root.destroy)
    quit_button.grid(row = 2, column = 0, columnspan = 5)

    # 创建功能按键
    image_transpose_button = ttk.Button(button_frame, text = "图像转置", command = image_transpose)
    image_transpose_button.grid(row = 1, column = 0)
    image_rotate_button = ttk.Button(button_frame, text = "图像旋转", command = click_rotate_button)
    image_rotate_button.grid(row = 1, column = 1)
    image_translate_button = ttk.Button(button_frame, text = "图像平移", command = click_translate_button)
    image_translate_button.grid(row = 1, column = 2)
    image_zoom_in_button = ttk.Button(button_frame, text = "图像放大", command = click_zoom_in_button)
    image_zoom_in_button.grid(row = 1, column = 3)
    image_zoom_out_button = ttk.Button(button_frame, text = "图像缩小", command = click_zoom_out_button)
    image_zoom_out_button.grid(row = 1, column = 4)

    # 创建图像Frame容器
    image_frame = ttk.Frame(canvas, padding = 10)
    image_frame.grid(row = 1, column = 0)
    canvas.create_window((1, 0), window = image_frame, anchor = "nw")

    root.mainloop()

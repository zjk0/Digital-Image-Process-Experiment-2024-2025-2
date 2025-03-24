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
@brief 显示图像
@param image_array: 图像数组
'''
def show_image (image_array):
    global transformed_image_tk

    # 转换
    image = Image.fromarray(image_array)
    transformed_image_tk = ImageTk.PhotoImage(image)

    # 显示转换后的图片
    transformed_image_label.config(image = transformed_image_tk)

'''
@brief “打开文件”按键的回调函数，打开文件选择界面，并对文件进行相应操作
@param none
'''
def file_operation ():
    pass

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
    quit_button.grid(row = 2, column = 0, columnspan = 5)

    # 创建功能按键

    # 创建图像标签
    origin_image_label = ttk.Label(frame)
    origin_image_label.grid(row = 1, column = 0)
    transformed_image_label = ttk.Label(frame)
    transformed_image_label.grid(row = 1, column = 1)

    # 创建图像标注
    origin_image_tip = ttk.Label(frame)
    origin_image_tip.grid(row = 2, column = 0)
    transformed_image_tip = ttk.Label(frame)
    transformed_image_tip.grid(row = 2, column = 1)

    # 创建一个布尔变量，判断“确定”按键是否按下
    bool_var = tk.BooleanVar()

    root.mainloop()
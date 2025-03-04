import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from PIL import Image
from PIL import ImageTk
import numpy as np
import struct

# 创建基本的图窗
root = tk.Tk()
root.title("数字图像处理实验二：图像文件读写")  # 设置图窗标题
frame = ttk.Frame(root, padding = 10)
frame.grid()

file_num = 0
file_index = 0

# 显示图片及其相关信息
def show_image (image_path):
    global image_tk  # 将与图窗相关的变量设置为全局变量，使得它们在图窗的作用域内
    image = Image.open(image_path)  # 通过图片路径打开图片
    image_tk = ImageTk.PhotoImage(image)  # 将图像转化为tkinter可用的PhotoImage对象

    # 显示图像
    image_label = ttk.Label(frame, image = image_tk)
    image_label.grid(row = 3, column = 0)

    # 显示图像大小
    image_size_label = ttk.Label(frame, text = f"图像大小：{image.size}")
    image_size_label.grid(row = 4, column = 0)

    # 显示图像类型
    image_mode_label = ttk.Label(frame)
    if image.mode == "RGB":
        image_mode_label.config(text = "图像类型：彩色图像")
    elif image.mode == "L":
        image_mode_label.config(text = "图像类型：灰度图像")
    image_mode_label.grid(row = 5, column = 0)

# 读取raw文件
def read_raw (file_name):
    pass

# 写入raw文件
def write_raw (file_name, array):
    pass

# 打开文件
def open_file ():
    file_path = fd.askopenfilename()

    # global file_num, file_index
    # file_num = len(file_path)

    # 获取文件格式
    format = []
    for i in reversed(range(len(file_path))):  # 从后往前遍历
        if file_path[i] == '.':  # 由于只需要文件格式，所以遇到'.'就退出循环
            break

        format.append(file_path[i])

    format.reverse()  # 将列表反装
    format_str = "".join(format)  # 将列表转化为字符串

    # 判断是否为raw文件，并进行相应的操作
    if format_str == "raw":
        pass
    else:
        show_image(file_path)

# 图窗中的提示
tip_1 = ttk.Label(frame, text = "如果只选了一张图像，那么只显示被选中的图像")
tip_1.grid(row = 0, column = 0)
tip_2 = ttk.Label(frame, text = "如果选中了多张图像，鼠标左键切换到上一张，右键切换到下一张，刚开始显示第一张")
tip_2.grid(row = 1, column = 0)

# 创建“打开文件”按键
open_file_button = ttk.Button(frame, text = "打开文件", command = open_file)  # 将按键的回调定位到open_file函数
open_file_button.grid(row = 2, column = 0)

# 创建“quit”按键
quit_button = ttk.Button(frame, text = "quit", command = root.destroy)
quit_button.grid(row = 6, column = 0)

root.mainloop()

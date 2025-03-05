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

file_num = 0  # 选取的文件的数量
file_index = 0  # 文件路径元组的索引

image_label = ttk.Label(frame)  # 用于显示图片的Label

''' 
读取raw文件 
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
写入raw文件 
'''
def write_raw (file_name, array):
    row, column = array.shape  # 获取二维数组各维的长度
    array_new = array.reshape(row * column)
    file_name_new = file_name[:len(file_name) - 4] + "_new" + file_name[len(file_name) - 4:]  # 创建一个新的文件名
    raw_file_new = open(file_name_new, "wb")  # 写入新的文件，每次都先清空再写入
    data = struct.pack(f"ii{row * column}B", column, row, *array_new)  # 数据转换
    raw_file_new.write(data)  # 写入数据
    raw_file_new.close()  # 关闭文件

''' 
显示图片及其相关信息 
'''
def show_image (image_path):
    global image_tk, image_label  # 将与图窗相关的变量设置为全局变量，使得它们在图窗的作用域内
    image = Image.open(image_path)  # 通过图片路径打开图片
    image_tk = ImageTk.PhotoImage(image)  # 将图像转化为tkinter可用的PhotoImage对象

    # 显示图像
    image_label.config(image = image_tk)
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

''' 
显示文件 
'''
def show_file ():
    global file_path, file, file_num, file_index, raw_image_tk, image_label

    # 获取要显示的文件
    file = file_path[file_index]

    # 获取文件格式
    format = []
    for i in reversed(range(len(file))):  # 从后往前遍历
        if file[i] == '.':  # 由于只需要文件格式，所以遇到'.'就退出循环
            break

        format.append(file[i])

    format.reverse()  # 将列表反装
    format_str = "".join(format)  # 将列表转化为字符串

    # 判断是否为raw文件，并进行相应的操作
    if format_str == "raw":
        raw_array = read_raw(file)  # 获取raw文件的图片的二维数组
        raw_image = Image.fromarray(raw_array)  # 二维数组转换为图片
        raw_image_tk = ImageTk.PhotoImage(raw_image)  # 转换为tkinter能够解析的PhotoImage类型

        # 显示raw文件的图片
        image_label.config(image = raw_image_tk)
        image_label.grid(row = 3, column = 0)

        # 显示图像大小
        raw_image_size_label = ttk.Label(frame, text = f"图像大小：{raw_image.size}")
        raw_image_size_label.grid(row = 4, column = 0)

        # 显示图像类型
        raw_image_mode_label = ttk.Label(frame, text = "图像类型：raw图像")
        raw_image_mode_label.grid(row = 5, column = 0)
        write_raw(file, raw_array)
    else:
        show_image(file)

''' 
显示下一张图片 
'''
def img_forward (event):
    global file_path, file, file_num, file_index
    file_index = (file_index + 1) % file_num  # 更新索引
    file = file_path[file_index]  # 获取要显示的文件
    show_file()  # 显示获取到的文件

''' 
显示上一张图片 
'''
def img_backward (event):
    global file_path, file, file_num, file_index

    # 更新索引
    if file_index == 0:
        file_index = file_num - 1
    else:
        file_index = (file_index - 1) % file_num

    # 显示获取到的文件
    show_file()

''' 
打开文件 
'''
def open_file ():
    global file_path, file, file_num, file_index, change_image_button
    file_path = fd.askopenfilenames()  # 获取文件路径
    file_num = len(file_path)  # 获取文件数量
    file_index = 0

    if file_num > 1:
        # 显示切换图片的按键
        change_image_button.grid(row = 6, column = 0)
    else:
        # 隐藏切换图片的按键
        change_image_button.grid_forget()

    # 显示获取到的文件
    show_file()

# 图窗中的提示
tip_1 = ttk.Label(frame, text = "如果只选了一张图像，那么只显示被选中的图像")
tip_1.grid(row = 0, column = 0)
tip_2 = ttk.Label(frame, text = "如果选中了多张图像，鼠标左键切换到上一张，右键切换到下一张，刚开始显示第一张")
tip_2.grid(row = 1, column = 0)

# 创建“打开文件”按键
open_file_button = ttk.Button(frame, text = "打开文件", command = open_file)  # 将按键的回调定位到open_file函数
open_file_button.grid(row = 2, column = 0)

# 创建用于鼠标交互的按键
change_image_button = ttk.Button(frame, text = "根据顶部的提示，点击我切换图片")
change_image_button.bind("<Button-1>", img_backward)  # 左键显示上一张图片
change_image_button.bind("<Button-3>", img_forward)  # 右键显示下一张图片

# 创建“quit”按键
quit_button = ttk.Button(frame, text = "quit", command = root.destroy)
quit_button.grid(row = 7, column = 0)

root.mainloop()

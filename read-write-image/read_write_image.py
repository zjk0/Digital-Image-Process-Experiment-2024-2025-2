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

# 显示图片
def show_image (image_path):
    global image_tk, image_label, image_information_label  # 将与图窗相关的变量设置为全局变量，使得它们在图窗的作用域内
    image = Image.open(image_path)  # 通过图片路径打开图片
    image_tk = ImageTk.PhotoImage(image)  # 将图像转化为tkinter可用的PhotoImage对象
    image_label = ttk.Label(frame, image = image_tk)
    image_label.grid(row = 1, column = 0)
    image_information_label = ttk.Label(frame, text = f"图像大小：{image.size}，图像类型：{image.mode}")  # 显示图像信息
    image_information_label.grid(row = 2, column = 0)

# 打开文件
def open_file ():
    file = fd.askopenfilename()
    if file:
        print("读取文件成功，文件路径为：" + file)
    else:
        print("读取文件失败，请确保文件存在或者文件未损坏")

    show_image(file)

# 创建“打开文件”按键
open_file_button = ttk.Button(frame, text = "打开文件", command = open_file)  # 将按键的回调定位到open_file函数
open_file_button.grid(row = 0, column = 0)

# 创建“quit”按键
quit_button = ttk.Button(frame, text = "quit", command = root.destroy)
quit_button.grid(row = 3, column = 0)

root.mainloop()

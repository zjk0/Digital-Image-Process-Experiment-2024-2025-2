import tkinter as tk
from tkinter import ttk
from PIL import Image
from PIL import ImageTk
import numpy as np

''' 创建表示图像的数组 '''
column = 512
row = 512

array_1 = np.zeros((column, row), dtype = np.uint8)        # 像素值全为0的灰度图像的数组，大小为512*512
array_2 = np.full((column, row), 255, dtype = np.uint8)    # 像素值全为255的灰度图像的数组，大小为512*512
array_3 = np.zeros((column, row), dtype = np.uint16)       # 像素值等于横坐标的灰度图像的数组，大小为512*512
array_4 = np.random.randint(0, 256, size = (column, row))  # 表示尽可能多色彩的彩色图像的数组，大小为512*512
array_5 = np.zeros((column, 32 * 9), dtype = np.uint8)     # 竖直条纹灰度图像的数组
array_3_fixed = np.zeros((column, row), dtype = np.uint8)  # 像素值等于横坐标的灰度图像的数组，大小为512*512

# 创建array_3
for i in range(column):
    array_3[:, i] = i

# 创建array_3_fixed
for i in range(column):
    array_3_fixed[:, i] = 255 * i / 512

# 创建array_5
for i in range(9):
    array_5[:, 32 * i : 32 * (i + 1)] = (32 * i) if i == 0 or i == 7 else (32 * i - 1)

''' 数组转化为图像 '''
image_1 = Image.fromarray(array_1, mode = "L")    # 像素值全为0的灰度图像
image_2 = Image.fromarray(array_2, mode = "L")    # 像素值全为255的灰度图像
image_3 = Image.fromarray(array_3, mode = "L")    # 像素值等于横坐标的灰度图像
image_4 = Image.fromarray(array_4, mode = "RGB")  # 尽可能多色彩的彩色图像
image_5 = Image.fromarray(array_5, mode = "L")    # 竖直条纹灰度图像的数组
image_3_fixed = Image.fromarray(array_3_fixed, mode = "L")

''' 创建GUI界面用于显示图片 '''
# 创建GUI图窗
root = tk.Tk()
frame = ttk.Frame(root, padding = 10)
frame.grid()

# 将图像转化为tkinter可用的PhotoImage对象
image_tk_1 = ImageTk.PhotoImage(image_1)
image_tk_2 = ImageTk.PhotoImage(image_2)
image_tk_3 = ImageTk.PhotoImage(image_3)
image_tk_4 = ImageTk.PhotoImage(image_4)
image_tk_5 = ImageTk.PhotoImage(image_5)
image_tk_3_fixed = ImageTk.PhotoImage(image_3_fixed)

# 显示图片
image_label_1 = ttk.Label(frame, image = image_tk_1)
image_label_1.grid(column =0 , row = 1)
image_label_2 = ttk.Label(frame, image = image_tk_2)
image_label_2.grid(column = 1, row = 1)
image_label_3 = ttk.Label(frame, image = image_tk_3)
image_label_3.grid(column = 2, row = 1)
image_label_4 = ttk.Label(frame, image = image_tk_4)
image_label_4.grid(column = 0, row = 3)
image_label_5 = ttk.Label(frame, image = image_tk_5)
image_label_5.grid(column = 1, row = 3)
image_label_3_fixed = ttk.Label(frame, image = image_tk_3_fixed)
image_label_3_fixed.grid(column = 2, row = 3)

# 为图片添加标注
style = ttk.Style()
style.configure("TLabel", font = ("宋体", 20))  # 设置字体和字体大小
image_text_1 = ttk.Label(frame, text = "灰度值全0", style = "TLabel")
image_text_1.grid(column = 0, row = 0)
image_text_2 = ttk.Label(frame, text = "灰度值全255", style = "TLabel")
image_text_2.grid(column = 1, row = 0)
image_text_3 = ttk.Label(frame, text = "像素值等于横坐标", style = "TLabel")
image_text_3.grid(column = 2, row = 0)
image_text_4 = ttk.Label(frame, text = "色彩尽可能多的彩色图", style = "TLabel")
image_text_4.grid(column = 0, row = 2)
image_text_5 = ttk.Label(frame, text = "竖直条纹灰度图", style = "TLabel")
image_text_5.grid(column = 1, row = 2)
image_text_3_fixed = ttk.Label(frame, text = "像素值等于横坐标 归一化平滑", style = "TLabel")
image_text_3_fixed.grid(column = 2, row = 2)

# 添加“退出”按键
button = ttk.Button(frame, text = "quit", command = root.destroy)
button.grid(column = 1, row = 4)

root.mainloop()

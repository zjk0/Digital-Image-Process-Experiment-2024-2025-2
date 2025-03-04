import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from PIL import Image
from PIL import ImageTk
import numpy as np
import struct

# root = tk.Tk()
# root.title("数字图像处理实验二：图像文件读写")  # 设置图窗标题
# frame = ttk.Frame(root, padding = 10)
# frame.grid()

# file_path = "D:\图像处理基础\实验\\bb\FILE20.raw"
# file = open(file_path, "rb")
# file_width = struct.unpack("i", file.read(4))[0]
# file_height = struct.unpack("i", file.read(4))[0]

# print(file_width)
# print(file_height)

# file_data = struct.unpack(f"{file_width * file_height}B", file.read())

# file.close()

# raw_array = np.array(file_data).reshape(file_height, file_width)

# raw_image = Image.fromarray(raw_array)
# raw_image_tk = ImageTk.PhotoImage(raw_image)

# raw_image_label = ttk.Label(frame, image = raw_image_tk)
# raw_image_label.grid(row = 0, column = 0)

# root.mainloop()

array = []
array.append('a')
array.append('b')
if "".join(array) == "ab":
    print("OK")
print(array)

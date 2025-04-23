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
@brief 显示变换后的图像
@param image_array: 图像数组
'''
def show_transform_image (image_array):
    global transform_image_tk

    # 转换
    image = Image.fromarray(np.uint8(image_array))
    transform_image_tk = ImageTk.PhotoImage(image)

    # 显示分割后的图片
    transform_image_label.config(image = transform_image_tk)

def morphology_process (image_array, method, dilation_se_size = 3, erosion_se_size = 3):
    # 获取图像行数和列数
    rows = image_array.shape[0]
    columns = image_array.shape[1]

    # 膨胀或者腐蚀
    if method == "dilation" or method == "erosion":
        # 获取结构元大小
        if method == "dilation":
            se_size = dilation_se_size
        elif method == "erosion":
            se_size = erosion_se_size

        # 边缘填充，采用零填充
        new_rows = rows + se_size - 1
        new_columns = columns + se_size - 1
        expand_array = np.zeros((new_rows, new_columns))
        offset = int((se_size - 1) / 2)
        expand_array[offset : rows + offset, offset : columns + offset] = np.copy(image_array)

        # 形态学处理
        se = np.ones((se_size, se_size))
        windows = sliding_window_view(expand_array, (se_size, se_size))
        if method == "dilation":
            result = np.max(np.multiply(windows[:, :], se), axis = (-2, -1))
        elif method == "erosion":
            result = np.min(np.multiply(windows[:, :], se), axis = (-2, -1))
    # 开运算或者闭运算
    elif method == "opening" or method == "closing":
        # 获取两个结构元大小
        if method == "opening":
            se_size_1 = erosion_se_size
            se_size_2 = dilation_se_size
        elif method == "closing":
            se_size_1 = dilation_se_size
            se_size_2 = erosion_se_size

        # 第一次边缘填充，采用零填充
        new_rows = rows + se_size_1 - 1
        new_columns = columns + se_size_1 - 1
        expand_array_1 = np.zeros((new_rows, new_columns))
        offset = int((se_size_1 - 1) / 2)
        expand_array_1[offset : rows + offset, offset : columns + offset] = np.copy(image_array)

        # 第一次形态学处理
        se_1 = np.ones((se_size_1, se_size_1))
        windows_1 = sliding_window_view(expand_array_1, (se_size_1, se_size_1))
        if method == "opening":  # 先进行腐蚀
            result = np.min(np.multiply(windows_1[:, :], se_1), axis = (-2, -1))
        elif method == "closing":  # 先进行膨胀
            result = np.max(np.multiply(windows_1[:, :], se_1), axis = (-2, -1))

        # 第二次边缘填充，采用零填充
        new_rows = rows + se_size_2 - 1
        new_columns = columns + se_size_2 - 1
        expand_array_2 = np.zeros((new_rows, new_columns))
        offset = int((se_size_2 - 1) / 2)
        expand_array_2[offset : rows + offset, offset : columns + offset] = np.copy(result)

        # 第二次形态学处理
        se_2 = np.ones((se_size_2, se_size_2))
        windows_2 = sliding_window_view(expand_array_2, (se_size_2, se_size_2))
        if method == "opening":  # 后进行膨胀
            result = np.max(np.multiply(windows_2[:, :], se_2), axis = (-2, -1))
        elif method == "closing":  # 后进行腐蚀
            result = np.min(np.multiply(windows_2[:, :], se_2), axis = (-2, -1))

    return result

def morphology_edge (image_array):
    image_array = morphology_process(image_array, "opening", dilation_se_size = 5, erosion_se_size = 5)
    transform_image_array = morphology_process(image_array, "erosion")
    result = image_array - transform_image_array
    return result

def connected_analysis (image_array):
    image_array = morphology_process(image_array, "opening", dilation_se_size = 5, erosion_se_size = 5)

    label_value = 0
    values = np.zeros(4, dtype = np.int32)
    labels = np.zeros(4, dtype = np.int32)
    equ_label = np.arange(image_array.shape[0] * image_array.shape[1])

    expand_array = np.pad(image_array, pad_width = 1, mode = 'constant', constant_values = 0)

    rows = expand_array.shape[0]
    columns = expand_array.shape[1]
    array_with_label = np.zeros((rows, columns, 2), dtype = np.int32)
    array_with_label[:, :, 0] = expand_array
    array_with_label[:, :, 1] = -1  # 表示未打标签

    for i in range(1, rows - 1):
        for j in range(1, columns - 1):
            if array_with_label[i, j, 0] == 255:
                values[0] = array_with_label[i, j - 1, 0]  # 左
                values[1] = array_with_label[i - 1, j - 1, 0]  # 左上
                values[2] = array_with_label[i - 1, j, 0]  # 上
                values[3] = array_with_label[i - 1, j + 1, 0]  # 右上
                labels[0] = array_with_label[i, j - 1, 1]
                labels[1] = array_with_label[i - 1, j - 1, 1]
                labels[2] = array_with_label[i - 1, j, 1]
                labels[3] = array_with_label[i - 1, j + 1, 1]

                if np.count_nonzero(values == 255) == 0:  # 周围没有前景点
                    array_with_label[i, j, 1] = label_value
                    label_value += 1
                else:  # 周围有前景点
                    if np.count_nonzero(labels != -1) == 0:  # 前景点都没有标签
                        array_with_label[i, j, 1] = label_value
                        array_with_label[i, j - 1, 1] = label_value if values[0] == 255 else (-1)
                        array_with_label[i - 1, j - 1, 1] = label_value if values[1] == 255 else (-1)
                        array_with_label[i - 1, j, 1] = label_value if values[2] == 255 else (-1)
                        array_with_label[i - 1, j + 1, 1] = label_value if values[3] == 255 else (-1)
                        label_value += 1
                    else:  # 有的前景点有标签
                        labels_1 = labels[labels != -1]
                        for k in range(labels_1.shape[0]):
                            # 寻找最小等价标签
                            while equ_label[labels_1[k]] != labels_1[k]:
                                labels_1[k] = equ_label[labels_1[k]]

                        min_label = np.min(labels_1)
                        
                        # 打标签
                        array_with_label[i, j, 1] = min_label
                        array_with_label[i, j - 1, 1] = min_label if (labels[0] == -1 and values[0] == 255) else labels[0]
                        array_with_label[i - 1, j - 1, 1] = min_label if (labels[1] == -1 and values[1] == 255) else labels[1]
                        array_with_label[i - 1, j, 1] = min_label if (labels[2] == -1 and values[2] == 255) else labels[2]
                        array_with_label[i - 1, j + 1, 1] = min_label if (labels[3] == -1 and values[3] == 255) else labels[3]

                        # 修改等价标签
                        equ_label[labels_1] = min_label
    
    # 第二次遍历
    for i in range(1, rows - 1):
        for j in range(1, columns - 1):
            if array_with_label[i, j, 0] == 255:
                # 寻找最小等价标签
                while equ_label[array_with_label[i, j, 1]] != array_with_label[i, j, 1]:
                    array_with_label[i, j, 1] = equ_label[array_with_label[i, j, 1]]

    # 彩色标注
    temp_array = np.zeros((rows, columns, 3), dtype = np.int32)
    rgb_array = np.random.randint(0, 256, (np.max(array_with_label[:, :, 1]) + 1, 3))
    for i in range(np.max(array_with_label[:, :, 1]) + 1):
        temp_array[array_with_label[:, :, 1] == i] = rgb_array[i]

    result = temp_array[1 : rows - 1, 1 : columns - 1]

    show_transform_image(result)
    transform_image_tip.config(text = f"8-领域连通域检测，有{label_value}个")

def image_morphology (method):
    global morphology_method, dilation_se_size, erosion_se_size, image_array

    morphology_method = method
    transform_image_array = morphology_process(image_array, method = morphology_method, dilation_se_size = dilation_se_size, erosion_se_size = erosion_se_size)
    
    show_transform_image(transform_image_array)

    scale_frame.grid(row = 3, column = 1)
    if method == "dilation":
        dilation_se_size_tip.grid(row = 0, column = 0)
        dilation_se_size_scale.grid(row = 0, column = 1)
        erosion_se_size_tip.grid_forget()
        erosion_se_size_scale.grid_forget()
        transform_image_tip.config(text = f"{morphology_method}处理后的图像, 结构元大小为{dilation_se_size}")
    elif method == "erosion":
        dilation_se_size_tip.grid_forget()
        dilation_se_size_scale.grid_forget()
        erosion_se_size_tip.grid(row = 1, column = 0)
        erosion_se_size_scale.grid(row = 1, column = 1)
        transform_image_tip.config(text = f"{morphology_method}处理后的图像, 结构元大小为{erosion_se_size}")
    elif method == "opening" or method == "closing":
        dilation_se_size_tip.grid(row = 0, column = 0)
        dilation_se_size_scale.grid(row = 0, column = 1)
        erosion_se_size_tip.grid(row = 1, column = 0)
        erosion_se_size_scale.grid(row = 1, column = 1)
        transform_image_tip.config(text = f"{morphology_method}处理后的图像, 腐蚀结构元大小为{erosion_se_size}, 膨胀结构元大小为{dilation_se_size}")

def get_image_morphology_edge ():
    global image_array
    edge = morphology_edge(image_array)
    show_transform_image(edge)
    scale_frame.grid_forget()
    transform_image_tip.config(text = "边界")

def update_dilation_se_size (se_size):
    global morphology_method, dilation_se_size, erosion_se_size, image_array

    dilation_se_size = int(se_size)
    transform_image_array = morphology_process(image_array, method = morphology_method, dilation_se_size = dilation_se_size, erosion_se_size = erosion_se_size)

    show_transform_image(transform_image_array)
    if morphology_method == "dilation":
        transform_image_tip.config(text = f"{morphology_method}处理后的图像, 结构元大小为{dilation_se_size}")
    elif morphology_method == "opening" or morphology_method == "closing":
        transform_image_tip.config(text = f"{morphology_method}处理后的图像, 腐蚀结构元大小为{erosion_se_size}, 膨胀结构元大小为{dilation_se_size}")

def update_erosion_se_size (se_size):
    global morphology_method, dilation_se_size, erosion_se_size, image_array

    erosion_se_size = int(se_size)
    transform_image_array = morphology_process(image_array, method = morphology_method, dilation_se_size = dilation_se_size, erosion_se_size = erosion_se_size)

    show_transform_image(transform_image_array)
    if morphology_method == "erosion":
        transform_image_tip.config(text = f"{morphology_method}处理后的图像, 结构元大小为{erosion_se_size}")
    elif morphology_method == "opening" or morphology_method == "closing":
        transform_image_tip.config(text = f"{morphology_method}处理后的图像, 腐蚀结构元大小为{erosion_se_size}, 膨胀结构元大小为{dilation_se_size}")

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
        image = Image.open(file_path).convert('L')
        _, _, image_array = get_image_data(image)

    # 转换为tkinter能解析的PhotoImage对象   
    origin_image_tk = ImageTk.PhotoImage(image)

    # 显示图像
    origin_image_label.config(image = origin_image_tk)
    origin_image_tip.config(text = "原图像")
    transform_image_label.config(image = "")
    transform_image_tip.config(text = "")
    scale_frame.grid_forget()

if __name__ == '__main__':
    # 初始化参数
    dilation_se_size = 3
    erosion_se_size = 3
    morphology_method = None

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
    open_file_button.grid(row = 0, column = 0, columnspan = 4)

    # 创建功能按键
    dilation_button = ttk.Button(button_frame, text = "膨胀", command = lambda: image_morphology("dilation"))
    dilation_button.grid(row = 1, column = 0)
    erosion_button = ttk.Button(button_frame, text = "腐蚀", command = lambda: image_morphology("erosion"))
    erosion_button.grid(row = 1, column = 1)
    opening_button = ttk.Button(button_frame, text = "开运算", command = lambda: image_morphology("opening"))
    opening_button.grid(row = 1, column = 2)
    closing_button = ttk.Button(button_frame, text = "闭运算", command = lambda: image_morphology("closing"))
    closing_button.grid(row = 1, column = 3)
    edge_button = ttk.Button(button_frame, text = "边界获取", command = get_image_morphology_edge)
    edge_button.grid(row = 2, column = 0, columnspan = 4)
    connected_analysis_button = ttk.Button(button_frame, text = "8-邻域连通域标记", command = lambda: connected_analysis(image_array))
    connected_analysis_button.grid(row = 3, column = 0, columnspan = 4)

    # 创建“退出”按键
    quit_button = ttk.Button(button_frame, text = "退出", command = root.destroy)
    quit_button.grid(row = 4, column = 0, columnspan = 4)

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
    dilation_se_size_tip = ttk.Label(scale_frame, text = "膨胀结构元大小: ")
    dilation_se_size_tip.grid(row = 0, column = 0)
    dilation_se_size_scale = tk.Scale(scale_frame, from_ = 3, to = 45, orient = "horizontal", length = 150, resolution = 2, command = update_dilation_se_size)
    dilation_se_size_scale.grid(row = 0, column = 1)
    dilation_se_size_scale.set(3)
    erosion_se_size_tip = ttk.Label(scale_frame, text = "腐蚀结构元大小: ")
    erosion_se_size_tip.grid(row = 1, column = 0)
    erosion_se_size_scale = tk.Scale(scale_frame, from_ = 3, to = 45, orient = "horizontal", length = 150, resolution = 2, command = update_erosion_se_size)
    erosion_se_size_scale.grid(row = 1, column = 1)
    erosion_se_size_scale.set(3)

    root.mainloop()
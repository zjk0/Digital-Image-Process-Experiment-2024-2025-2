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
@brief 获取灰度图像数据
@param image: PIL的Image类
@return image_array: 图像对应的二维数组
'''
def get_image_array (image):
    (width, height) = image.size  # 获取图像的宽和高
    image_array = np.array(image.getdata())  # 获取图像的像素数据并转化为数组
    image_array = image_array.reshape((height, width))
    return image_array

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
@brief 双线性插值
@param x1: 横轴插值范围的下界
@param y1: 纵轴插值范围的下界
@param x2: 横轴插值范围的上界
@param y2: 纵轴插值范围的上界
@param value11: (x1, y1)处的值
@param value12: (x1, y2)处的值
@param value21: (x2, y1)处的值
@param value22: (x2, y2)处的值
@param x: 插值点在横轴的位置
@param y: 插值点在纵轴的位置
@return result: 插值的计算结果
'''
def bilinear_interpolation (x1, y1, x2, y2, 
                            value11, value12, value21, value22, 
                            x, y):
    coef = 1 / ((x2 - x1) * (y2 - y1))
    vector1 = np.array([x2 - x, x - x1])
    matrix = np.array([[value11, value12], [value21, value22]])
    vector2 = np.array([[y2 - y], [y - y1]])
    result = coef * (vector1 @ matrix @ vector2)  # 使用@符号进行矩阵运算
    return result[0]

class GeometryTransform:
    '''
    @brief 初始化
    @param image_array: 需要进行变换的图像的数组
    '''
    def __init__ (self, image_array):
        self.origin_image_array = image_array  # 原图像数组

    '''
    @brief 图像绕其中心逆时针旋转90度
    @param self: GeometryTransform类对象本身
    @return transpose_image_array: 转置后的图像数组
    '''
    def image_transpose (self):
        transpose_image_array = self.origin_image_array.T
        return transpose_image_array

    '''
    @brief 图像绕其中心旋转
    @param self: GeometryTransform类对象本身
    @param angle: 旋转的角度，单位为度，正数表示逆时针旋转，负数表示顺时针旋转
    @return rotate_image_array: 旋转后的图像数组
    '''
    def image_rotate (self, angle):
        pass

    '''
    @brief 图像平移
    @param self: GeometryTransform类对象本身
    @param x_length: 在横轴方向上平移的长度，正负表示往正方向或负方向移动
    @param y_length: 在纵轴方向上平移的长度，正负表示往正方向或负方向移动
    @return translate_image_array: 平移后的图像数组
    '''
    def image_translate (self, x_length, y_length):
        # 获取图像数组的行数和列数
        rows = self.origin_image_array.shape[0]
        columns = self.origin_image_array.shape[1]

        translate_image_array = np.zeros((rows, columns))
        temp_array = np.zeros((rows, columns))  # 临时数组

        # 横轴移动
        if x_length > 0:
            temp_array[:, x_length : columns] = self.origin_image_array[:, 0 : columns - x_length]
        elif x_length < 0:
            temp_array[:, 0 : columns + x_length] = self.origin_image_array[:, -x_length : columns]
        else:
            temp_array[:, 0 : columns] = self.origin_image_array[:, 0 : columns]

        # 纵轴移动
        if y_length > 0:
            translate_image_array[y_length : rows, :] = temp_array[0 : rows - y_length, :]
        elif y_length < 0:
            translate_image_array[0 : rows + y_length, :] = temp_array[-y_length : rows, :]
        else:
            translate_image_array[0 : rows, :] = temp_array[0 : rows, :]

        return translate_image_array

    '''
    @brief 图像放大
    @param self: GeometryTransform类对象本身
    @param zoom_in_coef: 放大倍数，需要大于一
    @return zoom_in_image_array: 放大后的图像数组
    '''
    def image_zoom_in (self, zoom_in_coef):
        # 获取原始图像的行数和列数
        rows = self.origin_image_array.shape[0]
        columns = self.origin_image_array.shape[1]

        row_index = zoom_in_coef * np.arange(rows)
        column_index = zoom_in_coef * np.arange(columns)

        zoom_in_image_array = np.zeros((rows * zoom_in_coef, columns * zoom_in_coef))
        temp_array = np.zeros((rows * zoom_in_coef, columns * zoom_in_coef))
        pass

    '''
    @brief 图像缩小
    @param self: GeometryTransform类对象本身
    @param zoom_out_coef: 缩小倍数，需要大于一
    @return zoom_out_image_array: 缩小后的图像数组
    '''
    def image_zoom_out (self, zoom_out_coef):
        # 获取原图像的函数和列数
        rows = self.origin_image_array.shape[0]
        columns = self.origin_image_array.shape[1]

        zoom_out_image_array = np.zeros((rows, columns))
        temp_array = np.zeros((rows, columns))

        # 纵轴方向上的缩小
        for i in range(rows):
            if i * zoom_out_coef >= rows:
                break
            temp_array[i, :] = self.origin_image_array[i * zoom_out_coef, :]
        
        # 横轴方向上的缩小
        for i in range(columns):
            if i * zoom_out_coef >= columns:
                break
            zoom_out_image_array[:, i] = temp_array[:, i * zoom_out_coef]

        return zoom_out_image_array

'''
@brief 点击图像转置按键回调
@param none
'''
def click_transpose_button ():
    global geometry_transform, transformed_image_tk
    entry_frame.grid_forget()  # 隐藏参数输入框

    # 获取转置后的图像数组
    transpose_image_array = geometry_transform.image_transpose()

    # 显示转置后的图像
    transpose_image = Image.fromarray(transpose_image_array)  # 由数组得到Image对象
    transformed_image_tk = ImageTk.PhotoImage(transpose_image)  # 转换为tkinter能解析的PhotoImage对象
    transformed_image_label.config(image = transformed_image_tk)
    transformed_image_tip.config(text = "转置")

'''
@brief 点击图像旋转按键回调
@param none
'''
def click_rotate_button ():
    global geometry_transform, transformed_image_tk
    angle = 0  # 初始化angle变量
    entry_tip1.config(text = "旋转角度：")
    entry_tip2.grid_forget()  # 只需一个参数，隐藏第二个输入提示
    entry_area2.grid_forget()  # 只需一个参数，隐藏第二个输入框
    entry_frame.grid(row = 0, column = 1)

    '''
    @brief 确定旋转角度已经输入完毕并获取旋转角度
    @param none
    '''
    def click_certain_button ():
        nonlocal angle
        angle = float(entry_area1.get())  # 获取旋转角度
        bool_var.set(True)

    certain_button.config(command = click_certain_button)

    # 等待旋转角度输入完毕
    root.wait_variable(bool_var)
    bool_var.set(False)  # 复位bool_var

    # 隐藏输入参数部分并清空输入框
    entry_area1.delete(0, "end")
    entry_area2.delete(0, "end")
    entry_frame.grid_forget()

    # 获取旋转后的图像数组
    rotate_image_array = geometry_transform.image_rotate(angle)

    # 转换
    rotate_image = Image.fromarray(rotate_image_array)
    transformed_image_tk = ImageTk.PhotoImage(rotate_image)

    # 显示转换后的图片
    transformed_image_label.config(image = transformed_image_tk)
    transformed_image_tip.config(text = f"旋转角度为{angle}度")

'''
@brief 点击图像平移按键回调
@param none
'''
def click_translate_button ():
    global geometry_transform, transformed_image_tk
    x_length = 0  # 初始化横轴平移长度
    y_length = 0  # 初始化纵轴平移长度
    entry_tip1.config(text = "横轴平移长度：")
    entry_tip2.config(text = "纵轴平移长度：")
    entry_tip2.grid(row = 1, column = 0)
    entry_area2.grid(row = 1, column = 1)
    entry_frame.grid(row = 0, column = 1)

    '''
    @brief 确定平移参数已经输入完毕并获取旋转角度
    @param none
    '''
    def click_certain_button ():
        nonlocal x_length, y_length
        x_length = int(entry_area1.get())  # 获取横轴平移长度
        y_length = int(entry_area2.get())  # 获取纵轴平移长度
        bool_var.set(True)

    certain_button.config(command = click_certain_button)

    # 等待平移参数输入完毕
    root.wait_variable(bool_var)
    bool_var.set(False)  # 复位bool_var

    # 隐藏输入参数部分并清空输入框
    entry_area1.delete(0, "end")
    entry_area2.delete(0, "end")
    entry_frame.grid_forget()

    # 获取平移后的图像数组
    translate_image_array = geometry_transform.image_translate(x_length, y_length)

    # 转换
    translate_image = Image.fromarray(translate_image_array)
    transformed_image_tk = ImageTk.PhotoImage(translate_image)

    # 显示转换后的图片
    transformed_image_label.config(image = transformed_image_tk)
    transformed_image_tip.config(text = f"横轴平移长度为{x_length}, 纵轴平移长度为{y_length}")

'''
@brief 点击图像放大按键回调
@param none
'''
def click_zoom_in_button ():
    global geometry_transform, transformed_image_tk
    zoom_in_coef = 0  # 初始化放大倍数
    entry_tip1.config(text = "放大倍数：")
    entry_tip2.grid_forget()  # 只需一个参数，隐藏第二个输入提示
    entry_area2.grid_forget()  # 只需一个参数，隐藏第二个输入框
    entry_frame.grid(row = 0, column = 1)

    '''
    @brief 确定放大倍数已经输入完毕并获取旋转角度
    @param none
    '''
    def click_certain_button ():
        nonlocal zoom_in_coef
        zoom_in_coef = int(entry_area1.get())  # 获取放大倍数
        bool_var.set(True)

    certain_button.config(command = click_certain_button)

    # 等待放大倍数输入完毕
    root.wait_variable(bool_var)
    bool_var.set(False)  # 复位bool_var

    # 隐藏输入参数部分并清空输入框
    entry_area1.delete(0, "end")
    entry_area2.delete(0, "end")
    entry_frame.grid_forget()

    # 获取放大后的图像数组
    zoom_in_image_array = geometry_transform.image_zoom_in(zoom_in_coef)

    # 转换
    zoom_in_image = Image.fromarray(zoom_in_image_array)
    transformed_image_tk = ImageTk.PhotoImage(zoom_in_image)

    # 显示转换后的图片
    transformed_image_label.config(image = transformed_image_tk)
    transformed_image_tip.config(text = f"放大倍数为{zoom_in_coef}")

'''
@brief 点击图像缩小按键回调
@param none
'''
def click_zoom_out_button ():
    global geometry_transform, transformed_image_tk
    zoom_out_coef = 0  # 初始化缩小倍数
    entry_tip1.config(text = "缩小倍数：")
    entry_tip2.grid_forget()  # 只需一个参数，隐藏第二个输入提示
    entry_area2.grid_forget()  # 只需一个参数，隐藏第二个输入框
    entry_frame.grid(row = 0, column = 1)

    '''
    @brief 确定缩小倍数已经输入完毕并获取旋转角度
    @param none
    '''
    def click_certain_button ():
        nonlocal zoom_out_coef
        zoom_out_coef = int(entry_area1.get())  # 获取缩小倍数
        bool_var.set(True)

    certain_button.config(command = click_certain_button)

    # 等待缩小倍数输入完毕
    root.wait_variable(bool_var)
    bool_var.set(False)  # 复位bool_var

    # 隐藏输入参数部分并清空输入框
    entry_area1.delete(0, "end")
    entry_area2.delete(0, "end")
    entry_frame.grid_forget()

    # 获取缩小后的图像数组
    zoom_out_image_array = geometry_transform.image_zoom_out(zoom_out_coef)

    # 转换
    zoom_out_image = Image.fromarray(zoom_out_image_array)
    transformed_image_tk = ImageTk.PhotoImage(zoom_out_image)

    # 显示转换后的图片
    transformed_image_label.config(image = transformed_image_tk)
    transformed_image_tip.config(text = f"缩小倍数为{zoom_out_coef}")

'''
@brief “打开文件”按键的回调函数，打开文件选择界面，并对文件进行相应操作
@param none
'''
def file_operation ():
    global geometry_transform, origin_image_tk
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

    # 判断文件格式并得到Image对象
    if file_format_str == "raw":
        image_array = read_raw(file_path)
        image = Image.fromarray(image_array)
    else:
        image = Image.open(file_path)
        image_array = get_image_array(image)

    # 创建GeometryTransform类对象
    geometry_transform = GeometryTransform(image_array)

    # 转换为tkinter能解析的PhotoImage对象   
    origin_image_tk = ImageTk.PhotoImage(image)

    # 显示图像
    origin_image_label.config(image = origin_image_tk)
    origin_image_tip.config(text = "原图像")
    transformed_image_label.config(image = "")
    transformed_image_tip.config(text = "")

    # 隐藏输入框
    # bool_var.set(True)

if __name__ == '__main__':
    # 创建基本界面
    root = tk.Tk()
    root.title("数字图像处理实验五：几何变换")  # 设置界面标题
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
    image_transpose_button = ttk.Button(button_frame, text = "图像转置", command = click_transpose_button)
    image_transpose_button.grid(row = 1, column = 0)
    image_rotate_button = ttk.Button(button_frame, text = "图像旋转", command = click_rotate_button)
    image_rotate_button.grid(row = 1, column = 1)
    image_translate_button = ttk.Button(button_frame, text = "图像平移", command = click_translate_button)
    image_translate_button.grid(row = 1, column = 2)
    image_zoom_in_button = ttk.Button(button_frame, text = "图像放大", command = click_zoom_in_button)
    image_zoom_in_button.grid(row = 1, column = 3)
    image_zoom_out_button = ttk.Button(button_frame, text = "图像缩小", command = click_zoom_out_button)
    image_zoom_out_button.grid(row = 1, column = 4)

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

    # 创建用于输入参数的Frame
    entry_frame = ttk.Frame(frame, padding = 10)

    # 创建输入提示语
    entry_tip1 = ttk.Label(entry_frame)
    entry_tip1.grid(row = 0, column = 0)
    entry_tip2 = ttk.Label(entry_frame)
    entry_tip2.grid(row = 1, column = 0)

    # 创建参数输入框
    entry_area1 = ttk.Entry(entry_frame)
    entry_area1.grid(row = 0, column = 1)
    entry_area2 = ttk.Entry(entry_frame)
    entry_area2.grid(row = 1, column = 1)

    # 创建“确定”按键
    certain_button = ttk.Button(entry_frame, text = "确定")
    certain_button.grid(row = 2, column = 0, columnspan = 2)

    # 创建一个布尔变量，判断“确定”按键是否按下
    bool_var = tk.BooleanVar()

    root.mainloop()

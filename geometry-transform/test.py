# import tkinter as tk

# root = tk.Tk()

# tk.Label(root, text="欢迎使用").pack(pady=10)
# tk.Button(root, text="开始").pack(fill="x")
# tk.Button(root, text="设置").pack(fill="x")
# tk.Button(root, text="退出").pack(fill="x")

# root.mainloop()

########################################################################

# import tkinter as tk

# root = tk.Tk()

# tk.Label(root, text="用户名:").grid(row=0, column=0)
# tk.Entry(root).grid(row=0, column=1)
# tk.Label(root, text="密码:").grid(row=1, column=0)
# tk.Entry(root, show="*").grid(row=1, column=1)
# tk.Button(root, text="登录").grid(row=2, column=0, columnspan=2)

# root.mainloop()

###########################################################################

# import tkinter as tk

# root = tk.Tk()

# # 跨 3 列，标题居中
# tk.Label(root, text="欢迎使用系统", font=("Arial", 14)).grid(row=0, column=0, columnspan=3)

# tk.Button(root, text="功能 1").grid(row=1, column=0)
# tk.Button(root, text="功能 2").grid(row=1, column=1)
# tk.Button(root, text="功能 3").grid(row=1, column=2)

# root.mainloop()

##############################################################################

import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.geometry("500x400")

# 让 root 的行列可伸缩
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

# 创建 Canvas
canvas = tk.Canvas(root, bg="lightgray")
canvas.grid(row=0, column=0, sticky="nsew")

# 绑定垂直滚动条
scrollbar_y = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollbar_y.grid(row=0, column=1, sticky="ns")
canvas.config(yscrollcommand=scrollbar_y.set)

# 绑定水平滚动条
scrollbar_x = ttk.Scrollbar(root, orient="horizontal", command=canvas.xview)
scrollbar_x.grid(row=1, column=0, sticky="ew")
canvas.config(xscrollcommand=scrollbar_x.set)

# 创建 Frame 并嵌入 Canvas
frame = ttk.Frame(canvas, padding=10)
frame_window = canvas.create_window((0, 0), window=frame, anchor="nw")

# 让 frame 适应 Canvas 的宽度
def resize_frame(event):
    canvas_width = event.width  # 获取 Canvas 的当前宽度
    frame.config(width=canvas_width)  # 设置 Frame 的宽度等于 Canvas
    canvas.configure(scrollregion=canvas.bbox("all"))  # 更新滚动区域

canvas.bind("<Configure>", resize_frame)  # 绑定 Canvas 的大小变化事件

# 添加多个按钮（撑开 Frame）
for i in range(20):
    ttk.Button(frame, text=f"Button {i}").grid(row=i, column=0, padx=5, pady=5)

root.mainloop()


import tkinter as tk
from tkinter import ttk

import numpy as np
from matplotlib import pyplot as plt
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
from matplotlib.figure import Figure

root = tk.Tk()
frame = ttk.Frame(root, padding = 10)
frame.grid()

fig = Figure(figsize = (10, 5))
t = np.arange(0, 3, 0.01)
# ax = fig.add_subplot(1, 3, 1)
# line = ax.plot(t, 2 * np.sin(2 * np.pi * t))
# ax = fig.add_subplot(1, 3, 2)
# line = ax.plot(t, 2 * t)
# ax = fig.add_subplot(1, 3, 3)
# line = ax.plot(t, t * t)

canvas = FigureCanvasTkAgg(fig, frame)
canvas.draw()
canvas.get_tk_widget().grid(row = 0, column = 0)

toolbar = NavigationToolbar2Tk(canvas, frame, pack_toolbar = False)
toolbar.update()
toolbar.grid(row = 1, column = 0)

# 创建“quit”按键
quit_button = ttk.Button(frame, text = "quit", command = root.destroy)
quit_button.grid(row = 7, column = 0)

root.mainloop()

# array = np.random.randint(0, 10, (3, 4))
# array_1 = np.zeros((1, 4))
# print(array)
# print(array.shape[0])
# print(len(array.shape))
# print(array_1)
# print(array_1.shape)
# print(len(array_1.shape))

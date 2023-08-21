import tkinter as tk
from tkinter import ttk
import time

from constants import *

class ExportPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # main_frame = tk.Frame(self.controller, height=int(self.controller.hs*0.7))
        # main_frame.pack(fill=tk.BOTH, expand=1)

        # my_canvas = tk.Canvas(main_frame, height=int(self.controller.hs*0.7))
        # my_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # my_scrollbar = ttk.Scrollbar(main_frame, orient=tk.HORIZONTAL, command=my_canvas.xview)
        # my_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # my_canvas.configure(yscrollcommand=my_scrollbar.set)
        # my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion=my_canvas.bbox("all")))

        # second_frame = tk.Frame(my_canvas, height=int(self.controller.hs*0.7))
        # my_canvas.create_window((0,0), height=int(self.controller.hs*0.7), window=second_frame, anchor="nw")

        label = tk.Label(self, text="Save as...")
        label.grid(row=0, column=0)
        self.entry = tk.Entry(self, bd =5)
        self.entry.grid(row=0, column=1)
        btn = tk.Button(self, text='save', command=self.save_file)        
        btn.grid(row=1, columnspan=2, column=0)

    def save_file(self):
        self.controller.socket.sendto(SAVE_SIM, (UDP_IP, POWER_PORT))
        time.sleep(0.1)
        self.controller.socket.sendto(bytes(self.entry.get(),"utf-8"), (UDP_IP, POWER_PORT))
        time.sleep(0.1)
        self.controller.socket.sendto(self.controller.file_format, (UDP_IP, POWER_PORT))
        self.controller.on_closing(reset=True)




    




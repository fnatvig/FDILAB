import tkinter as tk
from tkinter import ttk
import struct

# from GUI.AttackPage1 import *
from constants import *


class GridModPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        main_frame = tk.Frame(self.controller, width=int(0.1*self.controller.ws))
        main_frame.pack(fill=tk.BOTH, expand=1)

        my_canvas = tk.Canvas(main_frame, width=int(0.1*self.controller.ws))
        my_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        my_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=my_canvas.yview)
        my_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        # my_scrollbar.pack(fill = tk.Y)

        my_canvas.configure(yscrollcommand=my_scrollbar.set)
        my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion=my_canvas.bbox("all")))

        second_frame = tk.Frame(my_canvas, width=int(0.1*self.controller.ws))
        my_canvas.create_window((0,0), width=int(0.1*self.controller.ws), window=second_frame, anchor="nw")

        header = tk.Label(second_frame, text="Line", width=len("Line")+15)
        header.grid(row=0, column = 0, columnspan=2)
        header = tk.Label(second_frame, text="Active")
        header.grid(row=0, column=2)
        # header = tk.Label(second_frame, text="Intensity")
        # header.grid(row=0, column=4)
        self.labels = []
        self.checkbox = []
        # self.sliders = []
        style = ttk.Style()
        style.configure("TScale", background="#505050")
        for i in range(0, len(self.controller.line_list)):
            self.labels.append(tk.Label(second_frame, text=f"{i}"))
            self.labels[i].grid(row=i+1, column=0, columnspan=2)
            self.checkbox.append(tk.Checkbutton(second_frame, onvalue=1, offvalue=0))
            self.checkbox[i].select()
            self.checkbox[i].grid(row=i+1, column=2)

        # width = len("Send Attack")
        # self.button1 = tk.Button(second_frame, text="Send Attack", command=lambda: self.send_attack())
        # self.button1.grid(row=len(self.controller.line_list)+1, column=3, columnspan=3, sticky='e'+'w')
        # self.button2 = tk.Button(second_frame, text="Undo Attack", command=lambda: self.undo_attack())
        # self.button2.grid(row=len(self.controller.line_list)+1, column=0, columnspan=3, sticky='e'+'w')
        # self.my_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.controller.geometry(f"{int(self.controller.ws*0.13)}x{int(self.controller.hs*0.25)}+{int(self.controller.ws/2)}+{int(self.controller.hs/9)}")
        
    def get_back(self):
        self.controller.reset_win()

    # def send_attack(self):
    #     for i in range(len(self.controller.line_list)):
    #         intensity = float(self.sliders[i].get())
    #         m_type = None
    #         if self.drops[i].get() == "Voltage":
    #             m_type = b'v'
    #         elif self.drops[i].get() == "P Consumption":
    #             m_type = b'p'
    #         elif self.drops[i].get() == "Q Consumption":
    #             m_type = b'q'
    #         if i < len(self.controller.line_list)-1:
    #             self.controller.socket.sendto(
    #                 struct.pack('i i s f', MULTI_BUS_ATTACK, i, m_type, intensity),
    #                 (UDP_IP, POWER_PORT))
    #         else:
    #             self.controller.socket.sendto(
    #                 struct.pack('i i s f', LAST_ATTACK_MSG, i, m_type, intensity),
    #                 (UDP_IP, POWER_PORT))

    # def undo_attack(self):
    #     for i in range(len(self.controller.line_list)):
    #         intensity = float(self.sliders[i].get())
    #         m_type = None
    #         if self.drops[i].get() == "Voltage":
    #             self.sliders[i].set(1.0)
    #             m_type = b'v'
    #         elif self.drops[i].get() == "P Consumption":
    #             self.drops[i].set("Voltage") 
    #             self.sliders[i].set(1.0)
    #             m_type = b'p'
    #         elif self.drops[i].get() == "Q Consumption":
    #             self.drops[i].set("Voltage")
    #             self.sliders[i].set(1.0)
    #             m_type = b'q'
    #         if i < len(self.controller.line_list)-1:
    #             self.controller.socket.sendto(
    #                 struct.pack('i i s f', MULTI_BUS_ATTACK, i, m_type, 1.0),
    #                 (UDP_IP, POWER_PORT))
    #         else:
    #             self.controller.socket.sendto(
    #                 struct.pack('i i s f', LAST_ATTACK_MSG, i, m_type, 1.0),
    #                 (UDP_IP, POWER_PORT))
        # self.controller.show_page(AttackPage1)
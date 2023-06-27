import tkinter as tk
from tkinter import ttk
import struct

from GUI.AttackPage1 import *
from constants import *


class ExportPage1(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        header = tk.Label(self, text="Element type")
        header.grid(row=0, column = 0, columnspan=2)
        header = tk.Label(self, text="Element")
        header.grid(row=0, column=2)
        header = tk.Label(self, text="Measurement Type")
        header.grid(row=0, column=4)
        
        self.labels = []
        self.drops = []
        self.sliders = []
        style = ttk.Style()
        style.configure("TScale", background="#505050")
        for i in range(0, len(self.controller.bus_list)):
            self.labels.append(tk.Label(self, text=f"{i}"))
            self.labels[i].grid(row=i+1, column=0, columnspan=2, padx=5)
            self.drops.append(ttk.Combobox(self, state="readonly", 
                                           values=["Voltage", "Active Power",
                                                   "Reactive Power"]))
            self.drops[i].set("Voltage")
            self.drops[i].grid(row=i+1, column=2)
            self.sliders.append(tk.Scale(self, from_=0.0, to=2.0, 
                                          orient=tk.HORIZONTAL, resolution=0.1)) 
            self.sliders[i].set(1.0)
            self.sliders[i].grid(row=i+1, column=4, pady=(0,15))

        width = len("Send Attack")
        self.button1 = tk.Button(self, text="Send Attack", command=lambda: self.send_attack())
        self.button1.grid(row=len(self.controller.bus_list)+1, column=0, columnspan=6, sticky='n'+'s'+'w'+'e')
        # self.update()
        # self.button2 = tk.Button(self, text="Back", command=lambda: self.get_back(), width=width)
        # self.button2.grid(row=len(self.controller.bus_list)+1, column=0, sticky='w')

    def get_back(self):
        self.controller.reset_win()

    def send_attack(self):
        for i in range(len(self.controller.bus_list)):
            bus = int(i)
            intensity = float(self.sliders[i].get())
            m_type = None
            if self.drops[i].get() == "Voltage":
                m_type = b'v'
            elif self.drops[i].get() == "Active Power":
                m_type = b'p'
            elif self.drops[i].get() == "Reactive Power":
                m_type = b'q'
            if i < len(self.controller.bus_list)-1:
                self.controller.socket.sendto(
                    struct.pack('i i s f', MULTI_BUS_ATTACK, i, m_type, intensity),
                    (UDP_IP, POWER_PORT))
            else:
                self.controller.socket.sendto(
                    struct.pack('i i s f', LAST_ATTACK_MSG, i, m_type, intensity),
                    (UDP_IP, POWER_PORT))

        # self.controller.show_page(AttackPage1)
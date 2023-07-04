import tkinter as tk
from tkinter import ttk
import struct

from constants import *


class ExportPage1(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.button1 = tk.Button(self, text="Export to excel", command=lambda: self.export_excel())
        self.button1.grid(row=1, column=0, columnspan=3, sticky='n'+'s'+'w'+'e', padx=5)

        self.button2 = tk.Button(self, text="Export to csv", command=lambda: self.export_csv())
        self.button2.grid(row=1, column=3, columnspan=3, sticky='n'+'s'+'w'+'e', padx=5)

    def get_back(self):
        self.controller.reset_win()

    def export_csv(self):
        self.controller.socket.sendto(EXPORT_CSV,(UDP_IP, POWER_PORT))
    
    def export_excel(self):
        self.controller.socket.sendto(EXPORT_EXCEL,(UDP_IP, POWER_PORT))
import tkinter as tk
import time

from constants import *

class ExportPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

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




    




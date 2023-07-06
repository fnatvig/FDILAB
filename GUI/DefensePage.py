import tkinter as tk
from tkinter import ttk
import os

from constants import *


class DefensePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        files = os.listdir('scripts')
        self.listbox = tk.Listbox(self)
        for file in files:
            self.listbox.insert(tk.END, file)
        self.listbox.select_set(0)
        self.listbox.grid(row=0, column=0, columnspan=2)
        btn = tk.Button(self, text='Activate chosen script', command=self.activate_script)        
        btn.grid(row=1, column=0)
        btn2 = tk.Button(self, text='Deactivate chosen script', command=self.deactivate_script)        
        btn2.grid(row=1, column=1)
    
    def activate_script(self):
        self.controller.socket.sendto(ACTIVATE_DEFENSE, (UDP_IP, POWER_PORT))
    
    def deactivate_script(self):
        self.controller.socket.sendto(DEACTIVATE_DEFENSE, (UDP_IP, POWER_PORT))
        # print(self.listbox.get(tk.ACTIVE))

    def get_back(self):
        self.controller.reset_win()

import tkinter as tk
import time
from socket import *
from multiprocessing import *

from constants import *



class CtrlPage4(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.startup = True
        # label = tk.Label(self, text="Page Two")
        # label.pack(side=tk.TOP)


        self.button1 = tk.Button(self, text="Exit", command=lambda: self.exit())
        self.button1.pack(expand=True, fill=tk.BOTH, side = tk.LEFT, padx=5, pady=self.controller.height/3)

        # self.button2 = tk.Button(self, text="Pause", command=lambda: self.pause_sim())
        # self.button2.pack(expand=True, fill=tk.BOTH, side = tk.RIGHT, padx=5, pady=self.controller.height/3)


        # self.button1["state"] = "disabled"
        # self.button2["state"] = "disabled"

    def exit(self):
        self.controller.on_closing()

        
import tkinter as tk
from socket import *
from multiprocessing import *

from constants import *

class SimCtrl3(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = tk.Label(self, text="Page Three")
        label.pack(pady=10, padx=10)

        button = tk.Button(self, text="Go to Page Two", command=lambda: self.controller.show_page(PageTwo))
        button.pack()
import tkinter as tk

from GUI.AttackPage1 import *
from GUI.AttackPage2 import *


class AttackWindow(tk.Tk):
    def __init__(self, bus_list):
        tk.Tk.__init__(self)
        container = tk.Frame(self)
        container.pack()
        self.bus_list = bus_list
        self.frames = {}
        for F in (AttackPage1, AttackPage2):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_page(AttackPage1)
        

    def show_page(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

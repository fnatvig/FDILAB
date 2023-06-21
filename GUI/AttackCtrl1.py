import tkinter as tk

from GUI.AttackCtrl2 import *
from GUI.AttackCtrl3 import *


class AttackCtrl1(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        container = tk.Frame(self)
        container.pack()
        self.frames = {}
        for F in (AttackCtrl2, AttackCtrl3):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_page(AttackCtrl2)
        

    def show_page(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

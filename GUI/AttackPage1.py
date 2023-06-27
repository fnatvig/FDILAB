import tkinter as tk

from GUI.AttackPage2 import *
from GUI.AttackPage3 import *

class AttackPage1(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        button1 = tk.Button(self, text="Single-bus Attack", command=lambda: self.single_attack())
        button1.pack(side=tk.LEFT, padx=10)
        button2 = tk.Button(self, text="Multi-bus Attack", command=lambda: self.multi_attack())
        button2.pack(side=tk.RIGHT, padx=10)


    def single_attack(self):
        # print(msg)
        self.controller.show_page(AttackPage2)

    def multi_attack(self):
        self.controller.show_page(AttackPage3)

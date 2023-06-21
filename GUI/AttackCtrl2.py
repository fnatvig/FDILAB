import tkinter as tk

from GUI.AttackCtrl3 import *

class AttackCtrl2(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = tk.Label(self, text="Page One")
        label.pack(pady=10, padx=10)


        button1 = tk.Button(self, text="btn1", command=lambda: self.send_msg("hej"))
        button1.pack()
        button2 = tk.Button(self, text="btn2", command=lambda: self.send_msg("då"))
        button2.pack()

    def send_msg(self, msg):
        print(msg)
        self.controller.show_page(AttackCtrl3)
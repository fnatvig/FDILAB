import tkinter as tk
from socket import *

from constants import *
from GUI.CtrlPage2 import *

class CtrlPage1(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = tk.Label(self, text="Page One")
        label.pack(pady=10, padx=10)


        button1 = tk.Button(self, text="Load case 14", command=lambda: self.send_msg(LOAD14))
        button1.pack()
        button2 = tk.Button(self, text="Load case 9", command=lambda: self.send_msg(LOAD9))
        button2.pack()

    def send_msg(self, msg):
        self.controller.socket.sendto(msg, (UDP_IP, POWER_PORT))
        if msg == LOAD14:
            self.controller.show_page(CtrlPage2)
        elif msg == LOAD9:
            self.controller.show_page(CtrlPage3)

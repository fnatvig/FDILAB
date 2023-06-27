import tkinter as tk
from socket import *

from constants import *
from GUI.CtrlPage2 import *

class CtrlPage1(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # label = tk.Label(self, text="Page One")
        # label.grid(row=0, column=1)

        button1 = tk.Button(self, text="Load case 14", command=lambda: self.send_msg(LOAD14))
        button1.grid(row=1, column=0, padx=10)
        button2 = tk.Button(self, text="Load case 9", command=lambda: self.send_msg(LOAD9))
        button2.grid(row=1, column=2, padx=10)

    def send_msg(self, msg):
        self.controller.socket.sendto(msg, (UDP_IP, POWER_PORT))
        if msg == LOAD14:
            self.controller.number_of_buses = 14
            self.controller.show_page(CtrlPage2)
        elif msg == LOAD9:
            self.controller.number_of_buses = 9
            self.controller.show_page(CtrlPage2)

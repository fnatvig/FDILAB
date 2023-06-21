import tkinter as tk
from socket import *

from constants import *
from GUI.SimCtrl2 import *

class SimCtrl1(tk.Frame):
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
        self.controller.show_page(SimCtrl2)
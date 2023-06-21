import tkinter as tk
from socket import *
from multiprocessing import *

from constants import *
from GUI.CtrlPage3 import *
from GUI.AttackWindow import *



class CtrlPage2(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = tk.Label(self, text="Page Two")
        label.pack(pady=10, padx=10)

        button1 = tk.Button(self, text="Start", command=lambda: self.send_msg(START_SIM))
        button1.pack()

        button2 = tk.Button(self, text="Pause", command=lambda: self.send_msg(PAUSE_SIM))
        button2.pack()

    def send_msg(self, msg):
        self.controller.socket.sendto(msg, (UDP_IP, POWER_PORT))
        if msg == START_SIM:
            bus_list = list(range(14)) 
            bus_list = [str(i) for i in bus_list]
            win = AttackWindow(bus_list)
        
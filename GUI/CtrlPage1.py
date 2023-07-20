import tkinter as tk
from socket import *

from constants import *
from GUI.CtrlPage2 import *

class CtrlPage1(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller


        button1 = tk.Button(self, text="Load case 14", command=lambda: self.send_msg(LOAD14))
        button1.pack(expand=True, fill=tk.BOTH, side = tk.LEFT, padx=5, pady=self.controller.height/3)
        button2 = tk.Button(self, text="Load case 9", command=lambda: self.send_msg(LOAD9))
        button2.pack(expand=True, fill=tk.BOTH, side = tk.RIGHT, padx=5, pady=self.controller.height/3)




    def send_msg(self, msg):
        self.controller.socket.sendto(msg, (UDP_IP, POWER_PORT))
        self.controller.sim_menu.entryconfig("Run Scenario", state="active")
        self.controller.scenario_menu.entryconfig("Run Scenario 1 (unattacked)", state="active")
        self.controller.scenario_menu.entryconfig("Run Scenario 1 (attacked)", state="active")
        self.controller.scenario_menu.entryconfig("Run Scenario 2 (unattacked)", state="active")
        self.controller.scenario_menu.entryconfig("Run Scenario 2 (attacked)", state="active")
        self.controller.sim_menu.entryconfig("Stop Simulation", state="active")
        self.controller.menubar.entryconfig("Window", state="active")

        if msg == LOAD14:
            self.controller.number_of_buses = 14
        elif msg == LOAD9:
            self.controller.number_of_buses = 9

        self.controller.show_page(CtrlPage2)


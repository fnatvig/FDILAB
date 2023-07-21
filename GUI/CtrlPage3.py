import tkinter as tk
import time
from socket import *
from multiprocessing import *

from constants import *
from GUI.AttackWindow import *
from GUI.DefenseWindow import *



class CtrlPage3(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.startup = True
        # label = tk.Label(self, text="Page Two")
        # label.pack(side=tk.TOP)


        self.button1 = tk.Button(self, text="Start", command=lambda: self.start_sim())
        self.button1.pack(expand=True, fill=tk.BOTH, side = tk.LEFT, padx=5, pady=self.controller.height/3)

        self.button2 = tk.Button(self, text="Pause", command=lambda: self.pause_sim())
        self.button2.pack(expand=True, fill=tk.BOTH, side = tk.RIGHT, padx=5, pady=self.controller.height/3)


        # self.controller.sim_menu.entryconfig("Export Simulation", state="disabled")
        # self.controller.export_menu.entryconfig("as .xlsx", state="active")
        # self.controller.export_menu.entryconfig("as .csv", state="active")

        self.button1["state"] = "disabled"
        self.button2["state"] = "active"



    def start_sim(self):
        self.controller.socket1.sendto(START_SIM, (UDP_IP, POWER_PORT))
        # self.controller.scenario_menu.entryconfig("Load Scenario", state="active")
        self.controller.sim_menu.entryconfig("Export Simulation", state="active")
        self.controller.export_menu.entryconfig("as .xlsx", state="active")
        self.controller.export_menu.entryconfig("as .csv", state="active")
        self.controller.menubar.entryconfig("Window", state="active")
        self.button1["state"] = "disabled"
        self.button2["state"] = "active"



    def pause_sim(self):
        self.controller.socket1.sendto(PAUSE_SIM, (UDP_IP, POWER_PORT))
        if (self.button1["state"] == "disabled"):
            self.button1["state"] = "active"
            self.button2["state"] = "disabled"
        
    
    # def export_data(self):
    #     self.controller.socket.sendto(SAVE_SIM, (UDP_IP, POWER_PORT))
    #     bus_list = [str(list(range(int(self.controller.number_of_buses)))[i]) for i in list(range(int(self.controller.number_of_buses)))]
    #     self.controller.export_win = ExportWindow(bus_list)            


        
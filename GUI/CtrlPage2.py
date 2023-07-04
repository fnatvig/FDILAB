import tkinter as tk
import time
from socket import *
from multiprocessing import *

from constants import *
from GUI.AttackWindow import *
from GUI.ExportWindow import *



class CtrlPage2(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.startup = True
        # label = tk.Label(self, text="Page Two")
        # label.pack(side=tk.TOP)

        self.button1 = tk.Button(self, text="Start", command=lambda: self.start_sim())
        self.button1.pack(side=tk.BOTTOM, padx=10)

        self.button2 = tk.Button(self, text="Pause", command=lambda: self.pause_sim())
        self.button2["state"] = "disabled"
        self.button2.pack(side=tk.BOTTOM, padx=10)

        self.button3 = tk.Button(self, text="Export data", command=lambda: self.export_data())
        self.button3["state"] = "disabled"
        self.button3.pack(side=tk.BOTTOM, padx=10)





    def start_sim(self):
        self.controller.socket.sendto(START_SIM, (UDP_IP, POWER_PORT))
        self.controller.menubar.entryconfig("Simulation", state="active")
        self.controller.menubar.entryconfig("Action", state="active")
        # time.sleep(2)
        self.button1["state"] = "disabled"
        self.button2["state"] = "active"

        # if (self.startup):
        #     self.startup = False
        #     self.button3["state"] = "active"
        #     bus_list = [str(list(range(int(self.controller.number_of_buses)))[i]) for i in list(range(int(self.controller.number_of_buses)))]
        #     self.controller.attack_win = AttackWindow(bus_list)


    def pause_sim(self):
        self.controller.socket.sendto(PAUSE_SIM, (UDP_IP, POWER_PORT))
        if (self.button1["state"] == "disabled"):
            self.button1["state"] = "active"
            self.button2["state"] = "disabled"
        
    
    def export_data(self):
        self.controller.socket.sendto(SAVE_SIM, (UDP_IP, POWER_PORT))
        bus_list = [str(list(range(int(self.controller.number_of_buses)))[i]) for i in list(range(int(self.controller.number_of_buses)))]
        self.controller.export_win = ExportWindow(bus_list)            


        
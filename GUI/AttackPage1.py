import tkinter as tk
from tkinter import ttk
from GUI.AttackPage2 import *

class AttackPage1(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = tk.Label(self, text="Bus: ")
        label.grid(row=0, column=0, pady=10)
        drop = ttk.Combobox(self, state="readonly",
                            values=self.controller.bus_list)
        drop.grid(row=0, column=1, pady=10)
        slider = tk.Scale(self, from_=0, to=2, orient=tk.HORIZONTAL)

        label = tk.Label(self, text="Measurement type: ")
        label.grid(row=1, column=0, pady=10)
        drop = ttk.Combobox(self, state="readonly",
                            values=["Voltage", 
                                    "Active Power", 
                                    "Reactive Power"])
        drop.grid(row=1, column=1, pady=10)
        label = tk.Label(self, text="Intensity: ")
        label.grid(row=2, column=0, pady=10)
        slider = tk.Scale(self, from_=0.0, to=2.0, orient=tk.HORIZONTAL, resolution=0.01)
        slider.grid(row=2, column=1)
        button1 = tk.Button(self, text="Send Attack", command=lambda: self.send_msg("hej"))
        button1.grid(row=3, columnspan=2)

    def send_msg(self, msg):
        print(msg)
        self.controller.show_page(AttackPage2)
import tkinter as tk
from tkinter import ttk
import struct

from GUI.AttackPage1 import *
from constants import *


class AttackPage2(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.controller.winfo_toplevel().title("FDIA")

        label = tk.Label(self, text="Bus: ")
        label.grid(row=0, column=0, pady=10)
        self.drop1 = ttk.Combobox(self, state="readonly",
                            values=self.controller.bus_list)
        self.drop1.grid(row=0, column=1, pady=10)

        label = tk.Label(self, text="Measurement type: ")
        label.grid(row=1, column=0, pady=10)
        self.drop2 = ttk.Combobox(self, state="readonly",
                            values=["Voltage", 
                                    "Active Power", 
                                    "Reactive Power"])
        self.drop2.grid(row=1, column=1, pady=10)
        label = tk.Label(self, text="Intensity: ")
        label.grid(row=2, column=0, pady=10)
        self.slider = tk.Scale(self, from_=0.0, to=2.0, orient=tk.HORIZONTAL, resolution=0.01)
        self.slider.set(1.0)
        self.slider.grid(row=2, column=1)
        self.button2 = tk.Button(self, text="Back", command=lambda: self.get_back())
        self.button2.grid(row=3, column=0)
        self.button1 = tk.Button(self, text="Send Attack", command=lambda: self.send_attack())
        self.button1.grid(row=3, column=1)

    def get_back(self):
        self.controller.reset_win()

    def send_attack(self):
        bus = int(self.drop1.get())
        intensity = float(self.slider.get())
        m_type = None
        if self.drop2.get() == "Voltage":
            m_type = b'v'
        elif self.drop2.get() == "Active Power":
            m_type = b'p'
        elif self.drop2.get() == "Reactive Power":
            m_type = b'q'
        self.controller.socket.sendto(
            struct.pack('i i s f', SINGLE_BUS_ATTACK, bus, m_type, intensity),
            (UDP_IP, POWER_PORT)
        )
